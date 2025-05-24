'''
負責幫助peer之間傳遞資料，不會儲存資料
'''
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import json
import queue
# 配置日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
class Client:
    pass
class Room:
    pass
class SocketServer:
    pass

class Client:
    def __init__(self, socket:socket.socket, host:str, port:int):
        self.host = host
        self.port = port
        self.socket = socket
        self.room:Room = None
        self.id = -1
        self.roomId = -1

    def join(self, room:Room, id:int, roomId:int):
        self.room = room
        self.id = id
        self.roomId = roomId

    def leave(self):
        self.room = None
        self.id = -1
        self.roomId = -1

    def getId(self):
        return self.id
    
    def isInRoom(self):
        return self.roomId != -1
    
class Room:
    def __init__(self, maxSize =4, roomId=48763):
        self.maxSize = maxSize
        self.size = 0
        self.clients:list[Client] = [None]*maxSize
        self.roomId = roomId

        self.lock = threading.Lock()

    def empty(self) -> bool:
        return self.size == 0
    
    def full(self) -> bool:
        return self.size == self.maxSize
    
    def join(self, client:Client):
        assert not self.full()
        with self.lock:
            id = self.find()
            self.clients[id] = client
            client.join(self, id, self.roomId)
            self.size += 1
        return
    
    def leave(self, client:Client):
        assert client.roomId == self.roomId
        with self.lock:
            id = client.getId()
            self.clients[id] = None
            client.leave()
            self.size -=1
        return 

    def find(self) -> int:
        assert not self.full()
        for i in range(self.maxSize):
            if self.clients[i] is None:
                return i
        logger.error('find room error')
    
    def allClients(self) -> list[Client]:
        return [client for client in self.clients if client != None]
    
    def getSize(self) -> int:
        return self.size

class SocketServer:
    def __init__(self, host='0.0.0.0', port=9999, max_threads=10):

        self.host = host
        self.port = port
        self.max_threads = max_threads
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.host, self.port))
        self.serverSocket.listen(max_threads)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_threads)
        logger.info(f"Server started on {self.host}:{self.port}")
        # p2p
        self.rooms:list[Room] = []
        self.lock = threading.Lock()

    def recvMsg(self, clientSocket:socket.socket, msgBuf:queue.Queue):
        if not msgBuf.empty():
            return msgBuf.get()
        raw = clientSocket.recv(65536)
        if not raw:
           raise Exception
        text = raw.decode('utf-8')
        for line in text.split('\n'):
            if not line:
                continue
            msgBuf.put(json.loads(line))
        return msgBuf.get()
    
    def sendMsg(self, msg:dict, clientSocket:socket.socket):
        data = json.dumps(msg, sort_keys=True, separators=(',', ':'))   + '\n'
        clientSocket.sendall(data.encode('utf-8'))

    def handle_client(self, clientSocket:socket.socket, client_address):
        msgBuf = queue.Queue()
        client = Client(socket= clientSocket,
                        host=client_address[0],
                        port=client_address[1])
        try:
            while True:
                
                msg = self.recvMsg(clientSocket,msgBuf)
                match msg["command"]:
                    case 'join':
                        self.join(client)
                    case 'leave':
                        self.leave(client)
                    case 'transfer':
                        msg1 = msg["msg"]
                        assert client.id == int(msg["from"])
                        peerIndex = int(msg["peerIndex"])
                        self.transfer(client=client, msg=msg1, peerIndex=peerIndex)

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            clientSocket.close()
            logger.info(f"Connection closed for {client_address}")


    
    def create(self, maxSize:int) -> Room:
        room = Room(maxSize=maxSize)
        self.rooms.append(room)
        return room
    
    def find(self) -> Room:
        for room in self.rooms:
            if not room.full():
                return room
        return None
    
    def join(self, client:Client):
        if client.isInRoom():
            return
        room = self.find()
        if room == None:
            room = self.create(maxSize=4)
        room.join(client)
        if room.full():
            for c in room.allClients():
                self.sendMsg({
                    'from':'-1',#server
                    'type':'server',
                    'msg':'someone join',
                    'number of people in room':room.getSize(),
                    'id': c.id,
                    'is full': room.full()
                }, c.socket)
                print(c.id)
        return
    
    def leave(self, client:Client):
        if not client.isInRoom():
            return
        room = client.room
        room.leave(client)
        self.sendMsg({
            'from':'-1',#server
            'msg':'leave success',
        }, client.socket)
        for c in room.allClients():
            self.sendMsg({
                'from':'-1',#server
                'msg':'someone leave',
                'number of people in room':room.getSize()
            }, c.socket)
    
    def transfer(self, client:Client, msg:dict, peerIndex:int):
        if not client.isInRoom():
            return
        room = client.room
        if peerIndex == -1:#boradcast
            for c in room.allClients():
                if c.id != client.id:
                    print(c.id, client.id)
                    self.sendMsg(msg, c.socket)
        else:
            peer = room.clients[peerIndex]
            self.sendMsg(msg, peer.socket)

    def run(self):
        try:
            while True:
                clientSocket, client_address = self.serverSocket.accept()
                self.thread_pool.submit(self.handle_client, clientSocket, client_address)
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.serverSocket.close()
            self.thread_pool.shutdown(wait=True)
    
if __name__ == "__main__":
    server = SocketServer(host='0.0.0.0', port=9999, max_threads=10)
    server.run()
