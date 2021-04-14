#________________________________________Thêm thư viện____________________________________________

import imagezmq
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import zmq
import base64

#________________________________________Khai báo_______________________________________________

#yolo
classes = ["người"]
net = cv2.dnn.readNetFromDarknet("yolov4-tiny-custom.cfg", "yolov4-tiny-custom_final.weights")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))
#send, recv image
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://169.254.99.118:3021") #két nối đến port 3021
socket.subscribe("")
#imageRecv = imagezmq.ImageHub(open_port = 'tcp://127.0.0.1:2345',REQ_REP= False)
#imageRecv = imagezmq.ImageHub(open_port = 'tcp://169.254.99.118:3021',REQ_REP= False)
imageSenderStream = imagezmq.ImageSender(connect_to = 'tcp://127.0.0.1:1998',REQ_REP = False)
imageSenderControl = imagezmq.ImageSender(connect_to = 'tcp://127.0.0.1:1203',REQ_REP = False)
#Crypto
keyAES = b"Sixteen byte key"
iv = b'0123456789abcdef'
cipherDecrypto = AES.new(keyAES, AES.MODE_CBC, iv)
#________________________________________Main()_______________________________________________

if __name__ == '__main__':

	while True:
		#msg,imgYolo = imageRecv.recv_image()
		imgBytes = socket.recv() # 
		encrypto = unpad(cipherDecrypto.decrypt(imgBytes), AES.block_size)
		nparr = np.frombuffer(encrypto, np.uint8)
		imgYolo = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
		height, width, channels = imgYolo.shape
		class_ids = []
		confidences = []
		boxes = []
		blob = cv2.dnn.blobFromImage(imgYolo, 1/255, (416, 416), (0, 0, 0), True, crop=False)
		net.setInput(blob)
		outs = net.forward(output_layers)
		for out in outs:
			for detection in out:
				scores = detection[5:]
				class_id = np.argmax(scores)
				confidence = scores[class_id]
				if confidence > 0:
					center_x = int(detection[0] * width)
					center_y = int(detection[1] * height)
					w = int(detection[2] * width)
					h = int(detection[3] * height)
					x = int(center_x - w / 2)
					y = int(center_y - h / 2)
					boxes.append([x, y, w, h])
					confidences.append(float(confidence))
					class_ids.append(class_id)
		indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
		font = cv2.FONT_HERSHEY_PLAIN
		havePerson = 0
		for i in range(len(boxes)):
			if i in indexes:
				havePerson = 1
				x, y, w, h = boxes[i]
				color = colors[class_ids[i]]
				cv2.rectangle(imgYolo, (x, y), (x + w, y + h), color, 2)
		imageSenderStream.send_image("yolo",imgYolo)
		if havePerson == 1:
			imageSenderControl.send_image(1,imgYolo)
		else:
			imageSenderControl.send_image(0,imgYolo)