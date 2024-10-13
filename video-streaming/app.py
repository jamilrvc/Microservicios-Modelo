from flask import Flask, render_template, request, send_from_directory, abort
import requests
import json, logging
from random import sample
from pymongo import MongoClient
import os


app = Flask(__name__)

os.environ.get('GUNICORN_BIND')

#Funciones

def get_database(dbhost,dbname):
   client = MongoClient(dbhost)
   return client.get_database(dbname)



# Configuración del canal de RabbitMQ
def connect_to_rabbitmq():
    logging.info(f"Connecting to RabbitMQ server at {RABBIT}.")
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    logging.info("Connected to RabbitMQ.")
    return channel

message_channel = connect_to_rabbitmq()

# Función para enviar mensaje a RabbitMQ
def send_viewed_message(message_channel, video_path):
    logging.info("Publishing message on 'viewed' queue.")
    msg = {"videoPath": video_path}
    json_msg = json.dumps(msg)
    message_channel.basic_publish(exchange='', routing_key='viewed', body=json_msg)
    logging.info(f"Message published: {json_msg}")



#path = "/video?path=SampleVideo_1280x720_1mb.mp4"
if os.environ.get('GUNICORN_BIND')==None:
    print("Hello world")



@app.route('/<path:path>',methods=['GET'])
def video_stream(path):
    if request.method == 'GET':
        try:
            video_response =  send_from_directory('static',  path)
            send_viewed_message(message_channel,path)
            return video_response
        except FileNotFoundError:
            abort(404)