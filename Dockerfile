FROM python:3.9.4-buster

WORKDIR /usr/src/c
COPY . .

RUN apt-get update 
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r requirements.txt

CMD python server.py

