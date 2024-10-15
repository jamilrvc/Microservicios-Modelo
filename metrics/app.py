from flask import Flask,jsonify, render_template, request, send_from_directory, abort
import requests, pika, json, logging
from random import sample
from pymongo import MongoClient
import os

# Variables de entorno

DBHOST = os.environ.get("DBHOST")
DBNAME = os.environ.get("DBNAME")
RABBIT = os.environ.get("RABBIT")
# Conectar con el servidor de la base de datos
client = MongoClient(DBHOST)

# Obtener la base de datos
db = client[DBNAME]

# Obtener la colección de estadistica de videos
metricCollection = db['metrics']
# Inicializar la aplicación Flask
app = Flask(__name__)


# Conexión a RabbitMQ y configuración del canal
def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT, port=5672,credentials=pika.PlainCredentials('guest', 'guest'), heartbeat= 600))
    channel = connection.channel()

    # Asegurar que el exchange "viewed" exista y si no lo crea
    channel.exchange_declare(exchange='viewed', exchange_type='fanout')
    return channel

message_channel = connect_rabbitmq()

# Función para manejar los mensajes de RabbitMQ
def process_rabbitmq_messages():

    queue_result = message_channel.queue_declare(queue='', exclusive=True)
    queue_name = queue_result.method.queue

    message_channel.queue_bind(exchange='viewed', queue=queue_name)

    def callback(ch, method, properties, body):
        print("Received a 'viewed' message")
        parsed_msg = json.loads(body.decode())
        logging.info(f"Received a 'viewed' message: {json.dumps(parsed_msg, indent=4)}")
        # Insertar en MongoDB el videoPath
        metricCollection.insert_one({'videoPath': parsed_msg['videoPath']})
        print(f"Added video {parsed_msg['videoPath']} to metrics.")
        
        # Acknowledge que el mensaje fue manejado
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info("Message acknowledged.")
    message_channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print("Waiting for messages. To exit press CTRL+C")
    message_channel.start_consuming()

process_rabbitmq_messages()

# Ruta GET para ver el estado del microservicio
@app.route("/", methods=['GET'])
def metrics():
   

    return "Microservice online"