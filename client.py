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
serverHost = '140.112.30.186'
serverPort = 9999

class Worker:
    # 每個worker只能處理一個socket
    STATUS_IDLE = 0
    STATUS_BUSY = 1
    STATUS_WAIT = 2

    def __init__(self, workerId: int, Worker2PoolQueue: queue.Queue):
        self.workerId = workerId
        # 主 pool -> Worker 任務隊列
        self.Pool2WorkerQueue: queue.Queue = queue.Queue()
        # Worker -> 主 pool 回報隊列
        self.Worker2PoolQueue: queue.Queue = Worker2PoolQueue
        self.status = Worker.STATUS_IDLE
        self.socketType = ''
        self.isConnect = False
        self.socket: socket.socket = None
        self.peerSocket: socket.socket = None
        self.peerIndex = -1
        self.peerHost = ''
        self.peerPort = -1

        self.cond = threading.Condition()

    def recvMsg(self) -> bytes:
        assert self.isConnect
        sock = self.socket if self.socketType == 'connect' else self.peerSocket
        return sock.recv(65536)

    def sendMsg(self, msg: dict) -> int:
        assert self.isConnect
        data = json.dumps(msg) + '\n'
        sock = self.socket if self.socketType == 'connect' else self.peerSocket
        sock.sendall(data.encode('utf-8'))
        return 1

    def setPeerInfo(self, peerIndex: int = -1, host: str = '', port: int = -1):
        self.peerIndex = peerIndex
        self.peerHost = host
        self.peerPort = port

    def createSocket(self, socketType: str):
        self.socketType = socketType
        self.isConnect = False
        self.status = Worker.STATUS_BUSY
        if socketType == 'connect':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('0.0.0.0', 0))
            self.socket.listen()

    def getListenAddr(self):
        assert self.socketType == 'listen'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 不用真的連，只是借用路由表來得知出站 IP
            s.connect(('8.8.8.8', 80))
            host = s.getsockname()[0]
        except Exception:
            host = '127.0.0.1'
        finally:
            s.close()

        port = self.socket.getsockname()[1]
        return host, port

    def tryConnection(self):
        try:
            if self.socketType == 'connect':
                print('try connect')
                print(self.peerHost, self.peerPort)
                self.socket.connect((self.peerHost, self.peerPort))
                print('connect ok')
                sock = self.socket
                
            else:
                sock, _ = self.socket.accept()
                
                self.peerSocket = sock
            self.isConnect = True
            self.Worker2PoolQueue.put({'from': self.workerId, 'data': {'command': 'connect_success', 'peerIndex': self.peerIndex}})
        except Exception as e:
            print('connect error')
            logger.error(f'Connection error: {e}')
            self.cleanup()
            self.status = Worker.STATUS_IDLE
            # 通知 pool 失敗
            self.Worker2PoolQueue.put({'from': self.workerId, 'data': {'command': 'connect_error', 'peerIndex': self.peerIndex}})

    def runLoop(self):
        while True:
            try:
                raw = self.recvMsg()
                if not raw:
                    break
                text = raw.decode('utf-8')
                for line in text.split('\n'):
                    if not line:
                        continue
                    payload = json.loads(line)
                    self.Worker2PoolQueue.put({'from': self.workerId, 'data': payload})
            except Exception as e:
                logger.error(f'Receive error: {e}')
                break
        self.cleanup()
        self.status = Worker.STATUS_IDLE

    def cleanup(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        if self.peerSocket:
            try:
                self.peerSocket.close()
            except:
                pass
        self.isConnect = False

    def run(self):
        self.tryConnection()
        
        if self.isConnect:
            logger.debug(f'connection success {self.peerIndex}')
            self.runLoop()
    


class SocketPool:
    def __init__(self, maxThreads=10):
        self.maxThreads = maxThreads
        self.Worker2PoolQueue = queue.Queue()
        self.threadPool = ThreadPoolExecutor(max_workers=self.maxThreads)
        self.workers:list[Worker] = [Worker(i, Worker2PoolQueue=self.Worker2PoolQueue) for i in range(self.maxThreads)]  # worker[0]連接到server
        self.Tpool2MainQueue = queue.Queue()  # 主函式要用的queue

    def find_free_worker(self) -> Worker:
        for worker in self.workers:
            if worker.status == Worker.STATUS_IDLE and worker.workerId != 0:
                worker.status = Worker.STATUS_BUSY
                return worker
        return None

    def findThreadwithPeerIndex(self, peerIndex) -> Worker:
        for worker in self.workers:
            if worker.status == Worker.STATUS_BUSY and worker.workerId != 0 and worker.peerIndex == peerIndex:
                return worker
        return None

    def p2pStart(self):
        self.p2pConstruct()
        self.threadPool.submit(self.tpoolStart)
        return self.Tpool2MainQueue, self.Worker2PoolQueue
    
    def tpoolStart(self):  # 處理所有thread的request
        def mainRequest(data):
            command = data["command"]
            if command == 'send':
                peerIndex = int(data["peerIndex"])

                message = data["message"]
                if peerIndex == -1:  # broadcast
                    for worker in self.workers:
                        if worker.status == Worker.STATUS_BUSY and worker.socketType != 'server':
                            worker.sendMsg(message)
                else:
                    worker = self.findThreadwithPeerIndex(peerIndex)
                    if worker:
                        worker.sendMsg(message)
        def p2pSocketRequest(msg):
            
            self.Tpool2MainQueue.put(msg)
            
        
        while True:
            msg = self.Worker2PoolQueue.get()
            logger.debug(f'tpool recv {msg}')
            workerId = int(msg["from"])
            if workerId == -1:  # 來自主程式的request
                mainRequest(msg["data"])
            else:  # from p2p thread
                p2pSocketRequest(msg["data"])

    def p2pConstruct(self):
        def checkConnectSuccess(workerId):
            msg, _ =self.getRequest(workerID=workerId)
            if msg["command"] == 'connect_success':
                return 1
            print('connect error')
            return 0
        #連線上server
        self.workers[0].createSocket(socketType='connect')
        self.workers[0].setPeerInfo(host=serverHost , port=serverPort)
        self.threadPool.submit(self.workers[0].run)
        if not checkConnectSuccess(0):
            return
        #step1 收到server的要求
        request, _ = self.getRequest(workerID=0) 
        if request["status"] != 200:
            return
        '''
            request={
                "status": 200,
                "msg": "table is full",
                "N": 4,
                "index": 2,
                "listen socket number": 2,
                "connect socket number": 1
            }
        '''
        self.index = request["index"]
        listenSocketNum = int(request["listen socket number"])
        connectSocketNum = int(request["connect socket number"])
        N = int(request["N"])

        listenSockets = []
        for peerIndex in range(listenSocketNum):
            freeWorker = self.find_free_worker()
            freeWorker.createSocket(socketType='listen')
            host, port = freeWorker.getListenAddr()
            freeWorker.setPeerInfo(peerIndex=peerIndex)
            self.threadPool.submit(freeWorker.run)
            listenSockets.append({
                "host": host,
                "port": port,
                "peerIndex": self.index,  # 寫給peer看的所以要反過來
                "index": peerIndex
            })
        # 回送給server
        self.workers[0].sendMsg({
            "status": 200,
            "msg": 'ok',
            "listenSockets": listenSockets
        })

        #收到server要求連線的清單
        request, _ = self.getRequest(workerID=0)
        '''request={
            'status':200,
            'msg':'ok'
            'connectSockets':[{
                'host':...,
                'port':...,
                'peerIndex':...,
                'index':...},
            ...]
        }'''
        for connectSocket in request["connectSockets"]:
            freeWorker = self.find_free_worker()
            freeWorker.createSocket(socketType='connect')
            freeWorker.setPeerInfo(peerIndex=int(connectSocket["peerIndex"]),
                                    host=connectSocket["host"],
                                    port=int(connectSocket["port"]))
            self.threadPool.submit(freeWorker.run)
        for i in range(N-1):
            checkConnectSuccess(-1)

        self.workers[0].sendMsg({
            "status":200,
            "msg":'p2pOk',
        })
            
        return

    def getRequest(self, workerID=-1):
        temp = []
        while True:
            msg = self.Worker2PoolQueue.get()
            if workerID == -1 or int(msg["from"]) == workerID:
                break
            temp.append(msg)
        for tempMsg in temp:
            self.Worker2PoolQueue.put(tempMsg)
        return msg["data"], int(msg["from"])
from signature import DigitalSignature

class p2pInterface():
    def __init__(self, isSignature = False):
        self.alreadyExchangePubKey = False
        self.isSignature = isSignature
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
        socketPool = SocketPool(maxThreads=10)
        self.Tpool2MainQueue, self.Main2TpoolQueue = socketPool.p2pStart()
        self.index = socketPool.index
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
            self.Main2TpoolQueue.put(msg)
        else:
            msg = {
                "from": -1,
                "data": {
                    "command": "send",
                    "peerIndex": peerIndex,  # Default to broadcast, can be changed by caller
                    "message": message
                }
            }
            self.Main2TpoolQueue.put(msg)

    def recvMsg(self, type=''):#若type不為空，則只接收type的訊息
        if type != '':
            temp = []
            while True:
                data = self.Tpool2MainQueue.get()
                '''
                有簽章的訊息
                data = {
                'index':
                'message':'message'<-要回傳的
                'signature'
                }
                '''
                if self.isSignature and self.alreadyExchangePubKey:
                    message = data["message"]
                else:
                    message = data
                if message["type"] == type:
                    break
                else:
                    temp.append(data)
            for temp_data in temp:
                self.Tpool2MainQueue.put(temp_data)
        else:
            data = self.Tpool2MainQueue.get()
        
        if self.isSignature and self.alreadyExchangePubKey:
            sig:str = data["signature"]
            message_json = json.dumps(data["message"], sort_keys=True)
            b64PubKey = self.PubKeyList[int(data["index"])]
            ok = self.digitalSignature.verify(sig, b64PubKey, message_json)
            if not ok:
                input('error signature')
            return data["message"]
        else:
            return data
    
    def getIndex(self):
        return self.index
    
    def signatureInit(self):
        self.alreadyExchangePubKey = 0
        self.digitalSignature = DigitalSignature()
        self.PubKeyList = [""]*4
        self.PubKey = self.digitalSignature.getPubKey()
        msg = {
            'type': 'signature public key',
            'index': self.index,
            'public key': self.PubKey
        }
        self.sendMsg(msg, peerIndex=-1)
        for _ in range(4-1):
            msg = self.recvMsg(type='signature public key')
            index = int(msg["index"])
            self.PubKeyList[index] = msg["public key"]
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