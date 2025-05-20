'''
client.py感覺有點像屎山代碼
thread之間或socket之間都是用json格式做溝通

worker:send和recv socket的訊息，處理socketpool的request, 把收到的訊息交給socketpool, 每個worker各開一個thread給他
socketpool:負責管理所有worker, 和處理p2pInterface的request
p2pinterface:主程式(bridge.py)和socket溝通的界面

架構大概會是
bridge --- p2pInterface --- socketPool --- worker
                                       --- worker
                                       --- worker
                                       --- worker
'''
import socket
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import json
import logging
logger = logging.getLogger(__name__)
serverHost = '0.0.0.0'
serverPort = 9999

def send_and_receive_json(socket, msg):
    send_json(socket, msg)
    
    return wait_json(socket)

def send_json(socket, msg):
    logger.debug(f'send {msg}')
    msg_json = json.dumps(msg)
    socket.sendall(msg_json.encode('utf-8'))

def wait_json(socket, size=1024*64):
    data = socket.recv(size)
    data = data.decode('utf-8')
    logger.debug(f'recv {data}')
    data = json.loads(data)
    return data

class worker:  # 每個worker只能處理一個socket
    def __init__(self, workerId, tpoolMsgQueue: queue.Queue):
        self.workerId = workerId
        self.msgQueue = queue.Queue()  # 接收提交的任務
        
        self.status = 0  # 0:空閒 1:使用中 2:等待
        self.tpoolMsgQueue = tpoolMsgQueue  # 回報結果
    def server_run(self, serverHost='0.0.0.0', serverPort=9999):
        self.connectType = 'server'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = self.socket.getsockname()
        self.socket.connect((serverHost, serverPort))
        data = wait_json(self.socket)
        if data['status'] != 200:
            return
        '''
            data={
                "status": 200,
                "msg": "table is full",
                "N": 4,
                "index": 2,
                "listen socket number": 2,
                "connect socket number": 1
            }
        '''
        # 跟tpool講要建立多少connect socket和listen socket
        listenSocketNum = int(data['listen socket number'])
        connectSocketNum = int(data['connect socket number'])
        index = int(data['index'])
        # 建立listen socket
        # 對所有id<自己的人
        # index=listenSocketNum
        listenSockets = []
        # 叫tpool創建socket和thread
        for peerIndex in range(listenSocketNum):
            
            # Convert string message to JSON format
            msg = {
                "command": "create",
                "type": "listen",
                "peerIndex": peerIndex,
                "index": index
            }

            
            self.tpoolMsgQueue.put(json.dumps({
                "from": self.workerId,
                "data": msg
            }))
        

        for i in range(listenSocketNum):
            msg_json = self.msgQueue.get()
            msg = json.loads(msg_json)
            host = msg["host"]
            port = msg["port"]
            peerIndex = msg["peerIndex"]
            index = msg["index"]
            listenSocket = {
                "host": host,
                "port": port,
                "peerIndex": index,  # 寫給peer看的所以要反過來
                "index": peerIndex
            }
            listenSockets.append(listenSocket)
        # 回送給server
        msg = {
            "status": 200,
            "msg": 'ok',
            "listenSockets": listenSockets
        }
        data = send_and_receive_json(self.socket, msg)
        if data['status'] != 200:
            return
        for connectSocket in data['connectSockets']:
            peerHost = connectSocket['host']
            peerPort = connectSocket['port']
            peerIndex = connectSocket['peerIndex']
            index = connectSocket['index']
            # Convert string message to JSON format
            msg = {
                "command": "create",
                "type": "connect",
                "host": peerHost,
                "port": peerPort,
                "peerIndex": peerIndex,
                "index": index
            }
            
            self.tpoolMsgQueue.put(json.dumps({
                "from": self.workerId,
                "data": msg
            }))
        #確定每個socket都成功連線
        for i in range(listenSocketNum+connectSocketNum):
            self.msgQueue.get()
        msg = {
            "command": "p2p success",
        }
        self.tpoolMsgQueue.put(json.dumps({
            "from": self.workerId,
            "data": msg
        }))

    def connect(self, peerHost, peerPort, peerIndex, index):
        logger.debug(f'connecting to {peerIndex}')
        self.socketType = 'connect'
        self.peerHost = peerHost
        self.peerPort = peerPort
        self.peerIndex = peerIndex
        self.index = index
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socket.connect((self.peerHost, self.peerPort))
            self.socket.sendall(b'hello')
            self.socket.recv(1024)
            logger.debug(f'connect to {peerIndex}')
        except Exception as e:
            print(f"Error: {e}")
            return
        #回報連線完成
        msg = {
            "command": "connect success",
            "peerIndex": self.peerIndex,
        }
        self.tpoolMsgQueue.put(json.dumps({
            "from": self.workerId,
            "data": msg
        }))
        while True:
            try:
                msg = self.socket.recv(1024*64)
                if msg == b'':
                    print('p2p error')
                    return
                msg_decoded = msg.decode('utf-8')
                logger.debug(f'recv msg {msg_decoded}')
                lines = [line for line in msg_decoded.split('\n') if line]

                for line in lines:
                    recv_msg = {
                        "command": "recv",
                        "peerIndex": peerIndex,
                        "message": line
                    }       
                    self.tpoolMsgQueue.put(json.dumps({
                        "from": self.workerId,
                        "data": recv_msg
                    }))
            except Exception as e:
                self.socket.close()
                print(f'Error {e}')
                return

    def listen(self, peerIndex, index):
        self.socketType = 'listen'
        self.peerIndex = peerIndex
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', 0))
        self.socket.listen(2)
        self.index = index
        self.host, self.port = self.socket.getsockname()
        # Convert string message to JSON format
        create_ok_msg = {
            "command": "create_ok",
            "type": "listen",
            "host": self.host,
            "port": self.port,
            "peerIndex": self.peerIndex,
            "index": index
        }
        
        self.tpoolMsgQueue.put(json.dumps({
            "from": self.workerId,
            "data": create_ok_msg
        }))
        logger.debug(f'start listening {peerIndex}')
        try: 
            self.peer_socket, self.peer_address = self.socket.accept()
            self.peer_socket.sendall(b'hello')
            self.peer_socket.recv(1024*64)
            logger.debug(f'listen to {peerIndex}')
        except Exception as e:
            print(f"Error: {e}")
            return
        #回報連線完成
        msg = {
            "command": "connect success",
            "peerIndex": self.peerIndex,
        }
        self.tpoolMsgQueue.put(json.dumps({
            "from": self.workerId,
            "data": msg
        }))
        while True:
            try:
                msg = self.peer_socket.recv(1024*64)
                if msg == b'':
                    print('p2p error')
                    return
                msg_decoded = msg.decode('utf-8')
                logger.debug(f'recv msg {msg_decoded}')
                lines = [line for line in msg_decoded.split('\n') if line]
                for line in lines:
                    recv_msg = {
                        "command": "recv",
                        "peerIndex": peerIndex,
                        "message": line
                    }       
                    self.tpoolMsgQueue.put(json.dumps({
                        "from": self.workerId,
                        "data": recv_msg
                    }))
            except Exception as e:
                self.socket.close()
                print(f'Error {e}')
                return

    def sendMsg(self, msg):
        msg = json.dumps(msg)
        if self.socketType == 'connect':
            self.socket.sendall(msg.encode('utf-8')+b'\n')
            return 1
        else:
            self.peer_socket.sendall(msg.encode('utf-8')+b'\n')
            return 1

class SocketPool:
    def __init__(self, maxThreads=10):
        self.maxThreads = maxThreads
        self.tpoolMsgQueue = queue.Queue()
        self.threadPool = ThreadPoolExecutor(max_workers=self.maxThreads)
        self.workers = [worker(i, self.tpoolMsgQueue) for i in range(self.maxThreads)]  # worker[0]連接到server
        self.mainQueue = queue.Queue()  # 主函式要用的queue

    def find_free_worker(self):
        for worker in self.workers:
            if worker.status == 0 and worker.workerId != 0:
                worker.status = 1
                return worker
        return None

    def p2pStart(self):
        self.cond = threading.Condition()
        self.threadPool.submit(self.tpoolStart)
        self.threadPool.submit(self.workers[0].server_run, serverHost, serverPort)
        with self.cond:#等待p2p連線完成
            self.cond.wait()
        print('p2p success')
        return self.tpoolMsgQueue, self.mainQueue

    def findThreadwithPeerIndex(self, peerIndex):
        for worker in self.workers:
            if worker.status == 1 and worker.workerId != 0 and worker.peerIndex == peerIndex:
                return worker
        return None

    def tpoolStart(self):  # 處理所有thread的request
        while True:

            msg_json = self.tpoolMsgQueue.get()
            logger.debug(f'tpool recv {msg_json}')
            msg = json.loads(msg_json)
            workerId = int(msg["from"])
            if workerId == -1:  # 來自主程式的request
                self.mainRequest(msg["data"])
            elif workerId == 0:  # from server thread
                self.serverSocketRequest(msg["data"])
            else:  # from p2p thread
                self.p2pSocketRequest(msg["data"])
    def mainRequest(self, data):
        command = data['command']
        if command == 'send':
            peerIndex = int(data["peerIndex"])

            message = data["message"]
            if peerIndex == -1:  # broadcast
                for worker in self.workers:
                    if worker.status == 1 and worker.socketType != 'server':
                        worker.sendMsg(message)
            else:
                worker = self.findThreadwithPeerIndex(peerIndex)
                if worker:
                    worker.sendMsg(message)
    def serverSocketRequest(self, msg):
        command = msg["command"]
        
        if command == "create":
            worker = self.find_free_worker()
            if not worker:
                print('no free worker')
                return 
            if msg["type"] == "listen":
                peerIndex = int(msg["peerIndex"])
                index = int(msg["index"])
                try:
                    self.threadPool.submit(worker.listen, peerIndex, index)
                    logger.debug('create thread')
                except Exception as e:
                    logger.error(f"Error: {e}")
                    return
                
            elif msg["type"] == "connect":
                host = msg["host"]
                port = int(msg["port"])
                peerIndex = int(msg["peerIndex"])
                index = int(msg["index"])
                try:
                    self.threadPool.submit(worker.connect, host, port, peerIndex, index)
                    logger.debug('create thread')
                except Exception as e:
                    logger.error(f"Error: {e}")
                    return
        
        elif command == "p2p success":
            with self.cond:
                self.cond.notify_all()
        else:
            print('msg error')

    def p2pSocketRequest(self, msg):
        command = msg["command"]
        if command == "create_ok":
            if msg["type"] == "listen":  # worker成功建立listen socket，跟worker[0]回報
                host = msg["host"]
                port = msg["port"]
                peerIndex = msg["peerIndex"]
                index = msg["index"]
                
                # Convert to JSON format when sending to worker[0]
                worker_msg = {
                    "host": host,
                    "port": port,
                    "peerIndex": peerIndex,
                    "index": index
                }
                self.workers[0].msgQueue.put(json.dumps(worker_msg))
            elif msg["type"] == "connect":
                pass
                # self.workers[0].tpoolMsgQueue.put(json.dumps({"status": "create successfully"}))
        elif command == "connect success":
            worker_msg = {
                "msg": "connect success",
                "peerIndex": msg["peerIndex"], 
            }
            self.workers[0].msgQueue.put(json.dumps(worker_msg))
        elif command == "recv":
            message = msg["message"]
            self.mainQueue.put(json.loads(message))
        elif command == "exit":
            print('exit')
        else:
            print(msg)
            print('msg error')

from signature import DigitalSignature

class p2pInterface():
    def __init__(self, isSignature = False):
        self.alreadyExchangePubKey = False
        self.isSignature = isSignature
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        socketPool = SocketPool(maxThreads=10)
        self.inputQueue, self.outputQueue = socketPool.p2pStart()
        self.index = socketPool.workers[1].index
        #數位簽章
        if self.isSignature:
            self.signatureInit()
        return
    
    def sendMsg(self, message, peerIndex = -1):
        # Input data is already in JSON format (dict)
        if 'type' not in message:
            print('Error: message must contain type')
            return
        if self.isSignature and self.alreadyExchangePubKey:#有簽章的話message需要再包一層
            msg = {
                "from": -1,
                "data": {
                    "command": "send",
                    "peerIndex": peerIndex,  # Default to broadcast, can be changed by caller
                    "message": self.wrapWithSignature(message)
                }
            }
            self.inputQueue.put(json.dumps(msg))
        else:
            msg = {
                "from": -1,
                "data": {
                    "command": "send",
                    "peerIndex": peerIndex,  # Default to broadcast, can be changed by caller
                    "message": message
                }
            }
            self.inputQueue.put(json.dumps(msg))

    def recvMsg(self, type=''):#若type不為空，則只接收type的訊息
        if type != '':
            temp = []
            while True:
                data = self.outputQueue.get()
                '''
                有簽章的訊息
                data = {
                'index':
                'message':'message'<-要回傳的
                'signature'
                }
                '''
                if self.isSignature and self.alreadyExchangePubKey:
                    message = data['message']
                else:
                    message = data
                if message['type'] == type:
                    break
                else:
                    temp.append(data)
            for temp_data in temp:
                self.outputQueue.put(temp_data)
        else:
            data = self.outputQueue.get()
        
        if self.isSignature and self.alreadyExchangePubKey:
            sig:str = data['signature']
            message_json = json.dumps(data['message'], sort_keys=True)
            b64PubKey = self.PubKeyList[int(data['index'])]
            ok = self.digitalSignature.verify(sig, b64PubKey, message_json)
            if not ok:
                input('error signature')
            return data['message']
        else:
            return data
    
    def getIndex(self):
        return self.index
    
    def signatureInit(self):
        self.alreadyExchangePubKey = 0
        self.digitalSignature = DigitalSignature()
        self.PubKeyList = ['']*4
        self.PubKey = self.digitalSignature.getPubKey()
        msg = {
            'type': 'signature public key',
            'index': self.index,
            'public key': self.PubKey
        }
        self.sendMsg(msg, peerIndex=-1)
        for _ in range(4-1):
            msg = self.recvMsg(type='signature public key')
            index = int(msg['index'])
            self.PubKeyList[index] = msg['public key']
        self.alreadyExchangePubKey = 1

    def wrapWithSignature(self, message: dict) -> dict:
        return {
            'index': self.index,
            'message': message,
            'signature': self.digitalSignature.signature(json.dumps(message, sort_keys=True))
        }

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
    socketPool = SocketPool(maxThreads=10)
    socketPool.p2pStart()
    while True:
        pass
