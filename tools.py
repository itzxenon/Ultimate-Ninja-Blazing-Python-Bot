# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import base64
import binascii
import StringIO

class PKCS7Encoder(object):
	def __init__(self, k=16):
	   self.k = k

	def decode(self, text):
		nl = len(text)
		val = int(binascii.hexlify(text[-1]), 16)
		if val > self.k:
			return text
		l = nl - val
		return text[:l]

	def encode(self, text):
		l = len(text)
		output = StringIO.StringIO()
		val = self.k - (l % self.k)
		for _ in xrange(val):
			output.write('00')#LITTLE FUCKER
		return text + binascii.unhexlify(output.getvalue())

class RijndaelEncryptor(object):
    def __init__(self):
        self.encoder=PKCS7Encoder()

    def encrypt(self, text, input_key, input_iv):
        key = input_key
        iv = input_iv
        aes = AES.new(key, AES.MODE_CBC, iv)
        pad_text = self.encoder.encode(text)
        cipher_text = aes.encrypt(pad_text)
        return base64.b64encode(cipher_text)
 
    def decrypt(self, text, input_key, input_iv):
        key = input_key
        iv = input_iv
        aes = AES.new(key, AES.MODE_CBC, iv)
        decode_text = base64.b64decode(text)
        pad_text = aes.decrypt(decode_text)
        return self.encoder.decode(pad_text)

class Crypter(object):
	def __init__(self):
		self.prmKey_128='78U#5e8!4@481eeU'
		self.prmIv_128='@#5U552&91127e)!'
		self.prmKey_256='lkirwf897+22#bbtrm8814z5qq=498j5'
		self.prmIv_256='741952hheeyy66#cs!9hjv887mxx7@8y'
		self.crypt=RijndaelEncryptor()

	def decode(self,text,version=1):
		if version==1:
			return self.crypt.decrypt(text,self.prmKey_128,self.prmIv_128)
		else:
			return self.crypt.decrypt(text,self.prmKey_256,self.prmIv_256)

	def encode(self,text,version=1):
		if version==1:
			return self.crypt.encrypt(text,self.prmKey_128,self.prmIv_128)
		else:
			return self.crypt.encrypt(text,self.prmKey_256,self.prmIv_256)