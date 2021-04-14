#________________________________________Thêm thư viện____________________________________________
from flask import Flask
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
import zmq
import os
import base64
from flask_sqlalchemy import SQLAlchemy
from Crypto import Random
#________________________________________Khai báo_______________________________________________
#send, recv name video
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:2456")
socket.subscribe("")
#crypto
keyAES = b'Sixteen byte key'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Video(db.Model):
    ten = db.Column(db.String(50), primary_key=True)
    thoigian = db.Column(db.String(20), nullable=False)
    mahoa = db.Column(db.String(2), nullable=False)
# _______________________________Funtion_________________________________________________________________
def decrypt(name):
	try:
		videoDir = "static/video/"+name
		videoBinary = open(videoDir, "rb").read()
		iv = videoBinary[:AES.block_size]
		cipherDecrypto = AES.new(keyAES, AES.MODE_CBC, iv)
		videoDecrypt = unpad(cipherDecrypto.decrypt(videoBinary[AES.block_size:]), AES.block_size)
		os.remove(videoDir)
		with open(videoDir,'wb') as file:
			file.write(videoDecrypt)	
	except:
		print(name)
	
def encrypt(name):
	videoDir = "static/video/"+name
	videoBinary = open(videoDir, "rb").read()
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(keyAES, AES.MODE_CBC,iv)
	videoEncrypt = cipher.encrypt(pad(videoBinary, AES.block_size))
	data = iv + videoEncrypt
	os.remove(videoDir)
	with open(videoDir,'wb') as file:
		file.write(data)
	video = Video.query.filter_by(ten= name).first()
	video.mahoa = '1'
	db.session.commit()
	print("oki")
#________________________________________Main()_______________________________________________
#threading.Thread(target=cryptoVideo).run()
if __name__ == '__main__':
	while True:
		nameVideo = socket.recv_string()
		encrypt(nameVideo)