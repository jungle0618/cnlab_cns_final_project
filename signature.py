from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import base64
class DigitalSignature:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=3,
            key_size=1024,
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