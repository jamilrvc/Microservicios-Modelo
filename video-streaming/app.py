from flask import Flask, render_template, request, send_from_directory, abort
import requests,pika, time
import json, logging
from random import sample
from pymongo import MongoClient
import os


app = Flask(__name__)

os.environ.get('GUNICORN_BIND')
RABBIT = os.environ.get("RABBIT")

#Funciones

def get_database(dbhost,dbname):
   client = MongoClient(dbhost)
   return client.get_database(dbname)



# Configuración del canal de RabbitMQ
def connect_to_rabbitmq():
    while True:
        try:
            logging.info(f"Connecting to RabbitMQ server at {RABBIT}.")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBIT,
                    port=5672,
                    credentials=pika.PlainCredentials('guest', 'guest'),
                    heartbeat=60  # 10 minutos de heartbeat
                )
            )
            channel = connection.channel()
            logging.info("Connected to RabbitMQ.")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
            time.sleep(5)
# Mantener la conexión a RabbitMQ
connection, message_channel = connect_to_rabbitmq()

# Función para enviar mensaje a RabbitMQ con verificación de conexión
def send_viewed_message(message_channel, video_path):
    try:
        if message_channel.is_open:
            logging.info("Publishing message on 'viewed' queue.")
            msg = {"videoPath": video_path}
            json_msg = json.dumps(msg)
            message_channel.basic_publish(exchange='', routing_key='viewed', body=json_msg)
            logging.info(f"Message published: {json_msg}")
        else:
            logging.warning("RabbitMQ channel closed, attempting to reconnect...")
            connection, message_channel = connect_to_rabbitmq()
            send_viewed_message(message_channel, video_path)
    except pika.exceptions.AMQPError as e:
        logging.error(f"Failed to publish message: {e}")
        connection, message_channel = connect_to_rabbitmq()
        send_viewed_message(message_channel, video_path)



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