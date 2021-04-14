
#________________________________________Thêm thư viện____________________________________________

import imagezmq
import cv2
import requests
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import ast
import zmq
import numpy as np
import time
import socket
#________________________________________Khai báo_______________________________________________

#imageSender = imagezmq.ImageSender(connect_to = 'tcp://127.0.0.1:2345',REQ_REP = False)
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:3021") # vô yolo
#mã hóa trao đổi công khai trên server 

#tạo khóa công khai
key = RSA.generate(1024) 
pubKey = key.publickey().exportKey("PEM")
#
url = 'http://127.0.0.1:5000/api/rsa'
response = requests.post(url, data=pubKey)
data = response.json().get('key')
rsa_private_key = PKCS1_OAEP.new(key)
keyAES = rsa_private_key.decrypt(ast.literal_eval(str(data)))#GIAIR MA BANG KHOA PRIVATE
print(keyAES)

iv = b'0123456789abcdef'   
cipher = AES.new(keyAES, AES.MODE_CBC,iv)
cipherDecrypto = AES.new(keyAES, AES.MODE_CBC, iv) 
#
#________________________________________Main()_______________________________________________

cap = cv2.VideoCapture(0) 
while True:
	ret, img = cap.read()
	if ret:
		_,image = cv2.imencode('.jpg',image)
		#imageSender.send_image('client',image)
		imgBytes = image.tobytes()
		imgEncrypto = cipher.encrypt(pad(imgBytes, AES.block_size))
		socket.send(imgEncrypto) # ảnh đã mã hóa sang yolo