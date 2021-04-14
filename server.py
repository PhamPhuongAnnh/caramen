
# _______________________________Thêm thư viện___________________________________________________________

from flask import Flask, render_template, Response, request
import cv2
import numpy as np
import threading
import time
import base64
from flask_socketio import SocketIO,emit
import jsonpickle
import os
#import imagezmq
#import subprocess
from flask_sqlalchemy import SQLAlchemy
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad  
# _______________________________Khai báo__________________________________________________________________

app = Flask(__name__)
#Stream
socketio = SocketIO(app,async_mode='threading')
countConnect = 0
#imageRecv = imagezmq.ImageHub(open_port = 'tcp://127.0.0.1:1998',REQ_REP= False)
#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Video(db.Model):
    ten = db.Column(db.String(50), primary_key=True)
    thoigian = db.Column(db.String(20), nullable=False)
    mahoa = db.Column(db.String(2), nullable=False)
#db.create_all()
class login(db.Model):
    email = db.Column(db.String(50),primary_key =  True)
    ten = db.Column(db.String(50),nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(50),nullable = False)

keyAES = b'Sixteen byte key'

# ______________________________API_______________________________________________________________________
#App
@app.route('/')
def index():
    return render_template('index.html')
#login
@app.route('/api/login')
def login():
    return render_template('login.html')
#sign up
@app.route('/api/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/api/streaming')
def streaming():
    return render_template('videostream.html')

@app.route('/api/videoplayback')
def videoplayback():
	videos = Video.query.filter_by(mahoa='1')
	return render_template('playback.html',videos=videos) 
@app.route('/api/rsa', methods=['POST'])
def rsa():
    global keyAES
    data = request.data
    pubKey = RSA.importKey(data)
    rsa_public_key = PKCS1_OAEP.new(pubKey)
    #mã hóa khóa AES
    aesKey = rsa_public_key.encrypt(keyAES)
    response = {'key': "{}".format(aesKey)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")
@app.route('/api/getVideo/<string:name>',methods=['GET','POST'])

def getVideo(name): # cái này là giải mã 
    global cipherDecrypto 
    videoDir = "static/video/{}".format(name) 
    try:
        with open(videoDir,'rb') as f:
            data = f.read()
            iv = data[:AES.block_size]
            cipherDecrypto = AES.new(keyAES, AES.MODE_CBC, iv)
            videoDecrypt = unpad(cipherDecrypto.decrypt(data[AES.block_size:]), AES.block_size)
            return base64.b64encode(videoDecrypt).decode('ascii')
    except IOError: # không mở được file video
        print("File not accessible")

#SocketIO
#Nếu có client connect
@socketio.on('connect')
def connectChannel():
    global countConnect
    countConnect+=1
#Nếu client disconnect
@socketio.on('disconnect')
def disconnectChannel():
    global countConnect
    if countConnect >0:
        countConnect-=1
    elif countConnect<0:
        countConnect=0

# _______________________________Funtion_________________________________________________________________

def thSendImg():
    global countConnect
  
    while True:
    	#nhận hình ảnh từ Yolo
    	msg,img = imageRecv.recv_image()
    	#encode ảnh
    	_,img_encode = cv2.imencode('.jpg',img)
    	#encode base64
    	img_64 = base64.b64encode(img_encode).decode('ascii')
    	#Nếu có client connect thì gửi ảnh
    	if countConnect>0 :
    		socketio.emit('imgChannel', {'data': img_64}, broadcast=True)
          
# _______________________________Main()__________________________________________________________________

if __name__ == '__main__':
    threading.Thread(target=thSendImg, daemon=True).start()
    socketio.run(app,host='0.0.0.0',port=os.getenv('PORT'))


