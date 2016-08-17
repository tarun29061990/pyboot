import base64

from Crypto import Random
from Crypto.Cipher import AES


# AES/CBC/PKCS5Padding encrypt
class AESEncryption(object):
    BLOCK_SIZE = 16

    def __pad(self, s):
        return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)

    def __unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def encrypt(self, raw, key):
        raw = self.__pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc, key):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = self.__unpad(cipher.decrypt(enc[16:]))
        return data.decode("utf8") if data else None
