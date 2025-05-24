
import socket
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from signature import DigitalSignature
logger = logging.getLogger(__name__)
#serverHost = '140.112.30.186'
serverHost = '0.0.0.0'
serverPort = 9999
maxThreads = 5

class Worker():
    def __init__(self, serverHost, serverPort, queue:queue.Queue):
        self.serverHost = serverHost
        self.serverPort = serverPort
        self.queue = queue
        self.isConnect = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.serverHost, self.serverPort))
        except Exception as e:
            logger.error(f'error {e}')
        self.isConnect = True

    def sendMsg(self, index=-1, peerIndex=-1, msg:dict={}): #peerIndex=-1為sendall
        assert self.isConnect
        msg1 = {
            'command':'transfer',
            'from':index,
            'peerIndex':peerIndex,
            'msg':msg
        }
        msg1 = json.dumps(msg1, sort_keys=True, separators=(',', ':'))  + '\n'
        self.socket.sendall(msg1.encode('utf-8'))

    def sendMsgtoServer(self, command:str):
        assert self.isConnect
        msg1 = {
            'command':command,
        }
        msg1 = json.dumps(msg1, sort_keys=True, separators=(',', ':'))  + '\n'
        self.socket.sendall(msg1.encode('utf-8'))


    def recvMsg(self) -> bytes:
        assert self.isConnect
        return self.socket.recv(65536)
    
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
                    self.queue.put(payload)
            except Exception as e:
                logger.error(f'Receive error: {e}')
                break
        self.cleanup()

    def cleanup(self):
        try:
            self.socket.close()
        except:
            pass
        self.isConnect = False

class p2pInterface():
    def __init__(self, peerNum=4, isSignature = False):
        self.peerNum = peerNum
        self.alreadyExchangePubKey = False
        self.isSignature = isSignature
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        #初始化tpool
        self.maxThreads = maxThreads
        self.threadPool = ThreadPoolExecutor(max_workers=self.maxThreads)
        self.queue = queue.Queue()
        #建立連線
        self.p2pStart()

        #數位簽章
        if self.isSignature:
            self.signatureInit()
        return
    
    def p2pStart(self):
        self.worker:Worker = Worker(serverHost=serverHost, serverPort=serverPort, queue=self.queue) 
        self.threadPool.submit(self.worker.runLoop)
        self.worker.sendMsgtoServer('join')
        while True:
            msg = self.recvMsg(type='server')
            if int(msg["is full"]):
                self.index = int(msg["id"])
                break
        logger.info(f'p2p finish')

    def sendMsg(self, message, peerIndex = -1):
        # Input data is already in JSON format (dict)
        if 'type' not in message:
            logger.error('Error: message must contain type')
            return
        if self.isSignature and self.alreadyExchangePubKey:#有簽章的話message需要再包一層
            self.worker.sendMsg(index=self.index, peerIndex=peerIndex, msg=self.wrapWithSignature(message))
        else:
            self.worker.sendMsg(index=self.index, peerIndex=peerIndex, msg=message)
            
    def recvMsg(self, type='') -> dict:#若type不為空，則只接收type的訊息
        while True:
            if type != '':
                temp = []
                while True:
                    data = self.queue.get()
                    '''
                    有簽章的訊息
                    data = {
                    'index':
                    'message':'message'<-要回傳的
                    'signature'
                    }
                    '''
                    
                    if self.isSignature and self.alreadyExchangePubKey:
                        if 'isSign' not in data:
                            temp.append(data)
                            continue
                        message = data["message"]
                    else:
                        if 'isSign' in data:
                            temp.append(data)
                            continue
                        message = data
                    if message["type"] == type:
                        break
                    else:
                        temp.append(data)
                for temp_data in temp:
                    self.queue.put(temp_data)
            else:
                data = self.queue.get()
            
            if self.isSignature and self.alreadyExchangePubKey:
                sig:str = data["signature"]
                message_json = json.dumps(data["message"], sort_keys=True, separators=(',', ':'))

                b64PubKey = self.PubKeyList[int(data["index"])]
                ok = self.digitalSignature.verify(sig, b64PubKey, message_json)
                if not ok:
                    
                    logger.error(f'error signature [{data["message"]}]')
                    
                    return -1
                return data["message"]
            else:
                return data
    
    def getIndex(self):
        return self.index
    
    def signatureInit(self):
        self.alreadyExchangePubKey = 0
        self.digitalSignature = DigitalSignature()
        self.PubKeyList = [""]*self.peerNum
        self.PubKey = self.digitalSignature.getPubKey()
        self.PubKeyList[self.index] = self.PubKey
        myUserId= self.digitalSignature.getUserId()
        msg = {
            'type': 'signature public key',
            'index': self.index,
            'user id': myUserId, 
            'public key': self.PubKey,
            'signature': self.digitalSignature.signature(f'userId: {myUserId}, index: {self.index}, public key: {self.PubKey}')
        }
        self.sendMsg(msg, peerIndex=-1)
        for _ in range(self.peerNum-1):
            msg = self.recvMsg(type='signature public key')
            index = int(msg["index"])
            
            userId = msg["user id"]
            sig = msg["signature"]
            otherpublicKey = msg["public key"]
            ok = self.digitalSignature.verify(sig, otherpublicKey, f'userId: {userId}, index: {index}, public key: {otherpublicKey}')
            if not ok:
                logger.error('error signature')
                continue
            self.PubKeyList[index] = otherpublicKey
        self.alreadyExchangePubKey = 1 #這步驟以後發送和驗證都會使用簽章
        #檢查所有人收到的publiclist是否一樣
        self.sendMsg({
            'type': 'check signature public key',
            'public list': self.PubKeyList,
            'from': self.index
        }, peerIndex=-1)
        temp = [False]*self.peerNum
        temp[self.index] = True
        while not all(temp):
            msg = self.recvMsg(type='check signature public key')
            otherPubKeyList = msg["public list"]
            index = int(msg["from"])
            if self.PubKeyList != otherPubKeyList:
                logger.error(f'error signature aaa')
                self.sendMsg({
                    'type': 'signature result',
                    'result': 'error'
                }, peerIndex=-1)
                return -1
            temp[index] = True
        #發送確認結果
        self.sendMsg({
            'type': 'signature result',
            'result': 'good',
            'from': self.index
        }, peerIndex=-1)
        temp = [False]*self.peerNum
        temp[self.index] = True
        while not all(temp):
            msg = self.recvMsg(type='signature result')
            result = msg["result"]
            index = int(msg['from'])
            if result != "good" or not(0<= index and index<self.peerNum):
                return -1
            temp[index] = True

    def wrapWithSignature(self, message: dict) -> dict:
        # 確保 message 是 deterministic（排序一致）
        message_str = json.dumps(message, sort_keys=True, separators=(',', ':'))  
        signature = self.digitalSignature.signature(message_str)
        return {
            'index': self.index,
            'message': message,
            'signature': signature,
            'isSign': 'True'
        }


