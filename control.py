#________________________________________Thêm thư viện____________________________________________

from flask import Flask
import imagezmq
import cv2
import numpy as np
import time
import threading
import smtplib
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
import zmq

#________________________________________Khai báo_______________________________________________

#Recv image
imageRecv = imagezmq.ImageHub(open_port = 'tcp://127.0.0.1:1203',REQ_REP= False)

#Save video
fourcc = cv2.VideoWriter_fourcc(*'H264')
saveVideo = None
#send name video
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:2456")
#Database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Video(db.Model):
    ten = db.Column(db.String(50), primary_key=True)
    thoigian = db.Column(db.String(20), nullable=False)
    mahoa = db.Column(db.String(2), nullable=False)
# _______________________________________Funtion_________________________________________________

def firstBlood(ten,now):
	thoigian = time.strftime("%H:%M:%S--%d/%m/%Y", now)
	"""
	message = "Có người xuất hiện lúc {} ".format(thoigian)
	msg = MIMEText(message, 'plain')
	msg['Subject']= "Cảnh báo!!!"
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login('kmafhnib@gmail.com','Lucifer98')
	server.sendmail('kmafhnib@gmail.com', 'fhnibkma@gmail.com', msg.as_string())
	server.quit()
	"""
	video = Video(ten = ten,thoigian = thoigian, mahoa = '0')
	db.session.add(video)
	db.session.commit()

#________________________________________Main()_______________________________________________

if __name__ == '__main__':
	sendMail = 0
	countOut = 0
	while True:
		msg,img = imageRecv.recv_image()
		if msg == 1:
			if sendMail == 1:
				saveVideo.write(img)
			else:
				now = time.localtime()
				timeString = time.strftime("%d%m%Y%H%M%S", now)
				nameVideo =  timeString + ".mp4"
				saveVideo = cv2.VideoWriter('static/video/{}'.format(nameVideo), fourcc, 12, (640, 480))
				saveVideo.write(img)
				sendMail = 1
				countOut = 120
				threading.Thread(target=firstBlood, args=(nameVideo, now)).run() #GỌI HÀM Ở TRÊN 
		else:
			countOut -= 1
			"""
			if countOut == 0:
				saveVideo.write(img)
				socket.send_string(nameVideo)
			"""
			if countOut > 0:
				saveVideo.write(img)
			else:
				if saveVideo is not None:
					saveVideo.release()
					saveVideo = None
					sendMail = 0
					socket.send_string(nameVideo)