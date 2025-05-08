import socket
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import json
serverHost='0.0.0.0'
serverPort=9999
def send_and_recieve_json(socket,msg):
    send_json(socket,msg)
    return wait_json(socket)
def send_json(socket,msg):
    msg_json = json.dumps(msg)
    socket.sendall(msg_json.encode('utf-8'))
def wait_json(socket):
    data = socket.recv(1024)
    #print(data)
    data=data.decode('utf-8')
    data = json.loads(data)
    return data
class worker:#每個worker只能處理一個socket
    def __init__(self, workerId, tpoolMsgQueue:queue.Queue):
        self.workerId = workerId
        self.msgQueue = queue.Queue()#接收提交的任務
        self.status = 0  # 0:空閒 1:使用中 2:等待
        self.tpoolMsgQueue = tpoolMsgQueue#回報結果
    def server_run(self,serverHost='0.0.0.0', serverPort=9999):
        self.connectType = 'server'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = self.socket.getsockname()
        self.socket.connect((serverHost, serverPort))
        data = wait_json(self.socket)
        if data['status']!=200:
            return
        '''
            data={
                "status": 200,
                "msg": "table is full",
                "N": 4,
                "index": 2,
                "listen socket number":2,
                "connect socket number":1
            }
        '''
        #跟tpool講要建立多少connect socket和listen socket
        listenSocketNum=int(data['listen socket number'])
        connectSocketNum=int(data['connect socket number'])
        index=int(data['index'])
        #建立listen socket
        #對所有id<自己的人
        #index=listenSocketNum

        listenSockets=[]
        #叫tpool創建socket和thread
        for peerIndex in range(listenSocketNum):
            self.tpoolMsgQueue.put(f'{self.workerId}:create:listen:{peerIndex}:{index}')
        for i in range(listenSocketNum):
            msg = self.msgQueue.get()
            msg = msg.split(':')
            host=msg[1]
            port=msg[2]
            peerIndex=msg[3]
            index=msg[4]
            listenSocket = {
                "host": host,
                "port": port,
                "peerIndex": index, #寫給peer看的所以要反過來
                "index": peerIndex
            }
            listenSockets.append(listenSocket)
        #回送給server
        msg={
            "status":200,
            "msg":'ok',
            "listenSockets":listenSockets
        }
        data = send_and_recieve_json(self.socket,msg)
        if data['status']!=200: return
        for connectSocket in data['connectSockets']:
            peerHost=connectSocket['host']
            peerPort=connectSocket['port']
            peerIndex=connectSocket['peerIndex']
            index=connectSocket['index']
            self.tpoolMsgQueue.put(f'{self.workerId}:create:connect:{peerHost}:{peerPort}:{peerIndex}:{index}')
    def connect(self,peerHost, peerPort, peerIndex, index):
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
            #print(f'connect to {self.peerIndex}')
        except Exception as e:
            print(f"Error: {e}")
            return
        while True:
            try:
                msg = self.socket.recv(1024)
                if msg == b'':
                    print('p2p error')
                    return
                #print(f'p2p recv [{msg}] from {self.peerIndex}')
                msg = msg.decode('utf-8')
                
                self.tpoolMsgQueue.put(f'{self.workerId}:recv:{peerIndex}:{msg}')
            except Exception:
                self.socket.close()
                print('error')
                return
    def listen(self, peerIndex, index):
        self.socketType = 'listen'
        self.peerIndex = peerIndex
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', 0))
        self.socket.listen(2)
        self.host, self.port = self.socket.getsockname()
        self.tpoolMsgQueue.put(f'{self.workerId}:create ok:listen:{self.host}:{self.port}:{self.peerIndex}:{index}')
        try:
            self.peer_socket, self.peer_address = self.socket.accept()
            self.peer_socket.sendall(b'hello')
            self.peer_socket.recv(1024)
            #print(f'listen to {self.peerIndex}')
        except Exception as e:
            print(f"Error: {e}")
            return
        while True:
            try:
                msg = self.peer_socket.recv(1024)
                if msg == b'':
                    print('p2p error')
                    return
                #print(f'p2p recv [{msg}] form {self.peerIndex}')
                msg = msg.decode('utf-8')
                
                self.tpoolMsgQueue.put(f'{self.workerId}:recv:{peerIndex}:{msg}')
            except Exception:
                self.socket.close()
                print('error')
                return
    def sendMsg(self, msg):
        #print(f'send [{msg}]')
        if self.socketType == 'connect':
            self.socket.sendall(msg.encode('utf-8'))
            return 1
        else:
            self.peer_socket.sendall(msg.encode('utf-8'))
            return 1
    
class SocketPool:
    def __init__(self, maxThreads=5):
        self.maxThreads = maxThreads
        self.msgQueue = queue.Queue()
        self.threadPool = ThreadPoolExecutor(max_workers=self.maxThreads)
        self.workers = [worker(i,self.msgQueue) for i in range(self.maxThreads)]#worker[0]連接到server
        self.mainQueue = queue.Queue()#主函式要用的queue
    def find_free_worker(self):
        for worker in self.workers:
            if worker.status == 0 and worker.workerId!=0:
                worker.status=1
                return worker
        return None
    def p2pStart(self):
        self.threadPool.submit(self.tpoolStart)
        self.threadPool.submit(self.workers[0].server_run, serverHost, serverPort)
        return self.msgQueue, self.mainQueue
    def findThreadwithPeerIndex(self, peerIndex):
        for worker in self.workers:
            if worker.status == 1 and worker.workerId!=0 and worker.peerIndex == peerIndex:
                return worker
        return None
    def tpoolStart(self):#處理所有thread的request
        while True:
            msg = self.msgQueue.get()
            msg=msg.split(':')
            workerId = int(msg[0])
            if workerId == -1:#來自主程式的request
                self.mainRequest(msg)
            elif workerId == 0:#from server thread
                self.serverSocketRequest(msg)
            else:#from p2p thread
                self.p2pSocketRequest(msg)
    def mainRequest(self,msg):
        peerIndex = int(msg[1])
        message = msg[2]
        if peerIndex==-1:#boradcast
            for worker in self.workers:
                if worker.status == 1 and worker.socketType!='server':
                    worker.sendMsg(message)
        else:
            worker = self.findThreadwithPeerIndex(peerIndex)
            worker.sendMsg(message)
    def serverSocketRequest(self,msg):
        match msg[1]:
            case 'create':
                worker = self.find_free_worker()
                if not worker:
                    print('no free worker')
                    return
                if msg[2] == 'listen':
                    peerIndex=int(msg[3])
                    index=int(msg[4])
                    self.threadPool.submit(worker.listen,peerIndex,index)
                elif msg[2] == 'connect':
                    host = msg[3]
                    port = int(msg[4])
                    peerIndex = int(msg[5])
                    index = int(msg[6])
                    self.threadPool.submit(worker.connect, host, port, peerIndex, index)
                
            case 'exit':
                print('exit')
            case _:
                print('msg error')
    def p2pSocketRequest(self, msg):
        match msg[1]:
            case 'create ok':
                if msg[2] == 'listen':#worker成功建立listen socket，跟worker[0]回報
                    host = msg[3]
                    port = msg[4]
                    peerIndex = msg[5]
                    index = msg[6]
                    self.workers[0].msgQueue.put(f'create ok:{host}:{port}:{peerIndex}:{index}')
                elif msg[2] == 'connect':
                    pass
                    #self.workers[0].msgQueue.put(f'create successfully')
            case 'recv':
                peerIndex = msg[2]
                message = msg[3]
                self.mainQueue.put(f'{peerIndex}:{message}')
            case 'exit':
                print('exit')
            case _:
                print('msg error')
        
def p2pRun():
    socketPool = SocketPool(maxThreads=5)
    inputQueue, outputQueue = socketPool.p2pStart()
    return inputQueue, outputQueue


