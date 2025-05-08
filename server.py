import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import json
import numpy as np
# 配置日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

N=3
def send_and_recieve_json(socket,msg):
    send_json(socket,msg)
    return wait_json(socket)
def send_json(socket,msg):
    msg_json = json.dumps(msg)
    socket.send(msg_json.encode('utf-8'))
def wait_json(socket):
    data = socket.recv(1024)
    print(data)
    data=data.decode('utf-8')
    data = json.loads(data)
    return data
class SocketServer:
    def __init__(self, host='0.0.0.0', port=9999, max_threads=5):
        self.host = host
        self.port = port
        self.max_threads = max_threads
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(max_threads)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_threads)
        logger.info(f"Server started on {self.host}:{self.port}")


        # p2p
        self.globalCond = threading.Condition()
        self.globalLock = threading.Lock()
        self.waitclientnum=0
        self.index=0
        self.waitclients={}
    def handle_client(self, client_socket, client_address):
        """處理單個客戶端連接"""
            #這裡完全沒鳥race condition
        try:
            client = {
                'ip': client_address[0],
                'port': client_address[1],
                'address': client_address,
                'status': 1,  # 1: 等待進入桌子 2: 等待收集 connect info
                'socket': client_socket,
                'index': self.index,
                'listenNumber': self.index,
                'connectNumber': N - 1 - self.index,
                'connectSockets': [],
                'cond_ready': threading.Condition(),       # 桌子滿了、可建立 socket
                'cond_socket_ready': threading.Condition() # 收到別人的 socket，可以發起連線
            }
            with self.globalLock:
                self.waitclients[self.index]=client
                self.waitclientnum+=1
                self.index+=1
            logger.info(f"New connection from {client_address}")
            if self.waitclientnum>=N:#湊到一桌
                for idx, otherclient in self.waitclients.items():
                    with otherclient['cond_ready']:
                        otherclient['cond_ready'].notify_all()
            else:
                client['status']=2
                with client['cond_ready']:
                    client['cond_ready'].wait()
            #有N個client連線
            msg={#告訴每個client需要建立多少listen和connect socket
                "status": 200,
                "msg": f"numbers of clients is enough",
                "N": N,
                "index": client['index'],
                "listen socket number":client['listenNumber'],
                "connect socket number":client['connectNumber']
            }
            # 等待client開啟socket
            data = send_and_recieve_json(client_socket,msg)
            if(data['status']!=200):
                logger.error(f"Error in client {client_address}: {data['msg']}")
                return
            #把自己收到的connect socket list交給其他thread，如果其他thread收到的connectSockets數量已經足夠，則叫醒其他thread
            with self.globalLock:
                for socket_info in data['listenSockets']:
                    print(f'a {client['index']}')
                    index = int(socket_info['index'])
                    otherclient=self.waitclients[index]
                    print(f'b {client['index']}')
                    otherclient['connectSockets'].append(socket_info)
                    print(f'c {client['index']}')
                    if len(otherclient['connectSockets'])>=otherclient['connectNumber']:
                        print(f'd {client['index']}')
                        with otherclient['cond_socket_ready']:
                            otherclient['cond_socket_ready'].notify_all()
                    print(f'e {client['index']}')
            print(f'hi{client['index']}')
            if len(client['connectSockets'])<client['connectNumber']:#當client還沒收到所有其他人的socket
                client['status']=2
                with client['cond_socket_ready']:
                    client['cond_socket_ready'].wait()
            #將client要連線的每個(host,port)回傳
            msg={}
            msg['status']=200
            msg['msg']='success'
            msg['connectSockets']=client['connectSockets']
            send_json(client['socket'],msg)
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Connection closed for {client_address}")


    def run(self):
        """主服務器循環，接受連接並提交到線程池"""
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                self.thread_pool.submit(self.handle_client, client_socket, client_address)
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.server_socket.close()
            self.thread_pool.shutdown(wait=True)

if __name__ == "__main__":
    server = SocketServer(host='0.0.0.0', port=9999, max_threads=5)
    server.run()