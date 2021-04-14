#________________________________________Import____________________________________________

import socket
import imagezmq
from picamera.array import PiRGBArray
from picamera import PiCamera
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
#_______________________________________________________________________________________
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 8
rawCapture = PiRGBArray(camera, size=(640, 480))
#imageSender = imagezmq.ImageSender(connect_to = 'tcp://169.254.99.118:3021',REQ_REP = False)
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://169.254.99.118:3021") 

addr = 'http://169.254.5.211:5000'
url = addr + '/api/rsa'
key = RSA.generate(1024)
pubKey = key.publickey().exportKey("PEM")
response = requests.post(url, data=pubKey)
data = response.json().get('key')
rsa_private_key = PKCS1_OAEP.new(key)
keyAES = rsa_private_key.decrypt(ast.literal_eval(str(data)))
print(keyAES)
iv = b'0123456789abcdef'
cipher = AES.new(keyAES, AES.MODE_CBC,iv)
cipherDecrypto = AES.new(keyAES, AES.MODE_CBC, iv)
#________________________________________Main()_______________________________________________

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array
	_,image = cv2.imencode('.jpg',image)
	#imageSender.send_image('client',image)
	imgBytes = image.tobytes()
	imgEncrypto = cipher.encrypt(pad(imgBytes, AES.block_size))
	socket.send(imgEncrypto)
	rawCapture.truncate(0)