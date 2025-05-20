from ecdsa.ellipticcurve import Point
from ecdsa.curves import SECP256k1
import secrets
import json
import client
import copy
curve = SECP256k1.curve
G = SECP256k1.generator
order = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class Protocol:
    def __init__(self, Pos, nPlayer:int=4, nCards:int=52):#
        self.Pos = Pos
        self.nextPos = (Pos+1)%nPlayer
        self.nPlayer = nPlayer
        self.nCards = nCards
        self.Key = int.from_bytes(secrets.token_bytes(32), "big")
        self.initP = [None]*nCards#還沒洗牌前每張牌應的點
        self.finalP = [None]*nCards#洗牌後每張牌應的點
        self.allP = [None]*nPlayer
        self.allK = [None]*nPlayer
        for i in range(nPlayer):
            self.allK[i] = [None]*nCards
            self.allP[i] = [None]*nCards
        #self.finalSuffle = [None]*nPlayer#finalSuffle[i]是洗完牌後的第i張牌原本的值
        for i in range(nCards):
            self.allK[self.Pos][i] = int.from_bytes(secrets.token_bytes(32), "big")
            self.allP[self.Pos][i] = int.from_bytes(secrets.token_bytes(32))*G
        self.id_to_val=[None]*nCards#id_to_val[3]=7表示洗完的牌從上面數下來第三張為7

    def encrypt(self, P, k):#P -> kP
        return k*P
    
    def decrypt(self, P, k):#P -> k^-1P
        return pow(k, -1, order)*P
    
    def shuffle1(self, cards:list):
        n = len(cards)
        for i in range(n):
            j = secrets.randbelow(n)
            cards[i], cards[j] = cards[j], cards[i]
        return cards
    
    def encryptCardsbyOneKey(self, cards:list):
        n = len(cards)
        for i in range(n):
            cards[i] = self.encrypt(cards[i], self.Key)
        return cards
    
    def decryptCardsbyOneKey(self, cards:list):
        n = len(cards)
        for i in range(n):
            cards[i] = self.decrypt(cards[i], self.Key)
        return cards
    
    def encryptCardsbyKey(self, cards:list):
        n = len(cards)
        for i in range(n):
            cards[i] = self.encrypt(cards[i], self.allK[self.Pos][i])
        return cards
    
    def decryptCardsbyKey(self, cards:list):
        n = len(cards)
        for i in range(n):
            cards[i] = self.decrypt(cards[i], self.allK[self.Pos][i])
        return cards
    
    def declarePoints(self, p2pInterface: client.p2pInterface):
        points = []
        Pos = self.Pos
        for i in range(self.nCards):
            points.append({
                'x': self.allP[Pos][i].x(),
                'y': self.allP[Pos][i].y(),
            })
        msg = {
            'status': 200,
            'type': 'declare point',
            'Pos': self.Pos,
            'points': points
        }
        p2pInterface.sendMsg(msg, -1)
        for i in range(self.nPlayer-1):
            msg = p2pInterface.recvMsg()
            Pos = int(msg['Pos'])
            points = msg['points']
            self.allP[Pos] = [None]*self.nCards
            for j in range(self.nCards):
                self.allP[Pos][j] = self.toPoint(points[j])
        for i in range(self.nCards):
            self.initP[i] = self.allP[0][i]
            for j in range(1, self.nPlayer):
                self.initP[i] = self.initP[i] + self.allP[j][i]
        

    def toPoint(self, point):
        return Point(curve, int(point['x']), int(point['y']))
    
    def toDict(self, point):
        return {
            'x': point.x(), 
            'y': point.y()
        }
    
    def shuffle(self, p2pInterface: client.p2pInterface):
        #先建立52個初始點
        self.declarePoints(p2pInterface)
        #用大K加密再洗牌後交給下個人
        if self.Pos == 0:
            cards = copy.deepcopy(self.initP)
        else:
            msg = p2pInterface.recvMsg()
            cards = [self.toPoint(card) for card in msg['cards']]
        cards = self.shuffle1(cards)
        cards = self.encryptCardsbyOneKey(cards)
        
        cards = [self.toDict(card) for card in cards]
        p2pInterface.sendMsg({
            'cards': cards,
            'type': 'shuffle',
        }, self.nextPos)
        #用自己的大K解密後用小k加密
        msg = p2pInterface.recvMsg()
        cards = [self.toPoint(card) for card in msg['cards']]
        cards = self.decryptCardsbyOneKey(cards)
        cards = self.encryptCardsbyKey(cards)
        cards = [self.toDict(card) for card in cards]
        #所有玩家都加密完後boradcast給所有人
        if self.nextPos == 0:
            p2pInterface.sendMsg({
            'cards': cards,
            'type': 'shuffle',
            },-1)
            self.finalP = [self.toPoint(card) for card in cards]

        else:
            p2pInterface.sendMsg({
            'cards': cards,
            'type': 'shuffle',
            },self.nextPos)
            msg = p2pInterface.recvMsg()
            self.finalP = [self.toPoint(card) for card in msg['cards']]
          
    def dealCards(self, p2pInterface: client.p2pInterface):#將牌發給每個人
        for Pos in range(self.nPlayer):
            if Pos == self.Pos:#自己拿牌
                IDs = [x for x in range(self.nCards) if x%self.nPlayer == self.Pos]
                self.getCards(p2pInterface, IDs)
            else:#別人拿牌
                self.otherGetCards(p2pInterface)
        return self.cards
    def getCards(self, p2pInterface: client.p2pInterface, IDs: list[int]):
        # 1. 广播“我要这几张牌”的请求
        req = {'type': 'request_keys', 'Pos': self.Pos, 'IDs': IDs}
        # 先把自己的 key 也放入 allK，以免收消息时漏掉自己
        for idx in IDs:
            # allK[self.Pos][idx] 已在 init 填好，无需改动
            pass
        p2pInterface.sendMsg(req, -1)

        # 2. 接收每个其他玩家发回的 provide_keys
        received = 0
        while received < self.nPlayer - 1:
            msg = p2pInterface.recvMsg()
            if msg['type'] != 'provide_keys':
                continue  # 跳过非预期消息
            sender = int(msg['Pos'])
            for item in msg['keys']:
                card_id = int(item['index'])
                key_k    = int(item['key'])
                self.allK[sender][card_id] = key_k
            received += 1

        # 3. 用 allK 的乘积解密
        self.cards = []
        for card_id in IDs:
            k_prod = 1
            for player in range(self.nPlayer):
                k_prod = (k_prod * self.allK[player][card_id]) % order
            P = self.finalP[card_id]
            P0 = self.decrypt(P, k_prod)
            if P0 in self.initP:
                card_val = self.initP.index(P0)
                self.id_to_val[card_id] = card_val
                self.cards.append(card_val)
            else:
                print(f"Card {card_id} 解密后不在 initP")

    def otherGetCards(self, p2pInterface: client.p2pInterface):
        # 一直循环监听请求，直到收到所有玩家的 request_keys
        received_reqs = 0
        while received_reqs < self.nPlayer - 1:
            msg = p2pInterface.recvMsg()
            if msg['type'] != 'request_keys':
                sender = int(msg['Pos'])
                for item in msg['keys']:
                    card_id = int(item['index'])
                    key_k    = int(item['key'])
                    self.allK[sender][card_id] = key_k
                received_reqs += 1
                continue
            requester = int(msg['Pos'])
            IDs = msg['IDs']
            # 把自己这份 small-k 发回给 requester
            resp = {
                'type': 'provide_keys',
                'Pos': self.Pos,
                'keys': [{'index': idx, 'key': self.allK[self.Pos][idx]} for idx in IDs]
            }
            p2pInterface.sendMsg(resp, -1)
            received_reqs += 1

    def playCards(self, p2pInterface: client.p2pInterface, card_val:int):#打出一張牌和關於他的key，給其他人驗證
        card_id = self.id_to_val.index(card_val)
        print(card_id, card_val)
        msg = {
            'type': 'play card',
            'Pos': self.Pos,
            'card_id': card_id,
            'key': self.allK[self.Pos][card_id],
            'card_val':card_val
        }
        p2pInterface.sendMsg(msg,-1)
    
        received_reqs = 0
        while received_reqs < self.nPlayer-1:
            msg = p2pInterface.recvMsg(type='check card')
            print(msg)
            if msg['msg'] == 'ok':
                received_reqs += 1
            else:
                print('play card_id error')
                received_reqs +=1
        return 1
    def otherplayCards(self, p2pInterface: client.p2pInterface):#回傳值和sender
        msg = p2pInterface.recvMsg(type='play card')
        card_id = int(msg['card_id'])
        card_val = int(msg['card_val'])
        key = int(msg['key'])
        sender = int(msg['Pos'])
        self.allK[sender][card_id] = key
        k_prod = 1
        for player in range(self.nPlayer):
            k_prod = (k_prod * self.allK[player][card_id]) % order
        P = self.finalP[card_id]
        P0 = self.decrypt(P, k_prod)
        if P0 == self.initP[card_val]:
            p2pInterface.sendMsg(
                {
                    'type': 'check card',
                    'msg': 'ok'
                },
                peerIndex= sender
            )
            return card_val, sender
        else:
            p2pInterface.sendMsg(
                {
                    'type': 'check card',
                    'msg': 'not ok'
                },
                peerIndex = sender
            )
            return -1, sender

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import base64
class DigitalSignature:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )  # RSA 安全性來源於大質數分解困難度 :contentReference[oaicite:2]{index=2}

        # 從私鑰取得公鑰並序列化
        self.public_key = self.private_key.public_key()
        pem_pub = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.b64PubKey = base64.b64encode(pem_pub).decode('utf-8')

    def getPubKey(self) -> str:
        return self.b64PubKey
    
    def signature(self, message:str) -> str:
        messageEncode = message.encode('utf-8')
        sig = self.private_key.sign(
            messageEncode,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')
    def verify(self, sig_b64: str, pKey_b64: str, msg: str):
        try:
            # 還原簽章
            sig = base64.b64decode(sig_b64)

            # 還原公鑰物件
            from cryptography.hazmat.primitives import serialization
            pKey_bytes = base64.b64decode(pKey_b64.encode('utf-8'))
            public_key = serialization.load_pem_public_key(pKey_bytes)

            # 編碼訊息
            msg_bytes = msg.encode('utf-8')

            # 驗證
            public_key.verify(
                sig,
                msg_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print("簽章驗證成功：訊息完整且發送者可信")
            return True
        except InvalidSignature:
            print("簽章驗證失敗：可能遭到篡改或冒用")
            return False
        except Exception as e:
            print("驗證錯誤：", e)
            return False