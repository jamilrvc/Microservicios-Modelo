from flask import Flask,jsonify, render_template, request, send_from_directory, abort
import requests, pika, json
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

# Obtener la colección de historial
historyCollection = db['history']
# Inicializar la aplicación Flask
app = Flask(__name__)


# Conexión a RabbitMQ y configuración del canal
def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT, port=5672,credentials=pika.PlainCredentials('guest', 'guest'), heartbeat= 600))
    channel = connection.channel()

    # Asegurar que la cola "viewed" exista
    channel.queue_declare(queue='viewed')
    return channel

message_channel = connect_rabbitmq()

# Función para manejar los mensajes de RabbitMQ
def process_rabbitmq_messages():
    def callback(ch, method, properties, body):
        print("Received a 'viewed' message")
        parsed_msg = json.loads(body.decode())
        
        # Insertar en MongoDB el videoPath
        historyCollection.insert_one({'videoPath': parsed_msg['videoPath']})
        print(f"Added video {parsed_msg['videoPath']} to history.")
        
        # Acknowledge que el mensaje fue manejado
        ch.basic_ack(delivery_tag=method.delivery_tag)

    message_channel.basic_consume(queue='viewed', on_message_callback=callback)
    print("Waiting for messages. To exit press CTRL+C")
    message_channel.start_consuming()

# Iniciar consumo de mensajes de RabbitMQ en un hilo separado
import threading
rabbitmq_thread = threading.Thread(target=process_rabbitmq_messages)
rabbitmq_thread.daemon = True
rabbitmq_thread.start()

# Ruta GET para recuperar el historial de videos vistos
@app.route("/history", methods=['GET'])
def get_history():
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({"error": "skip and limit must be integers"}), 400

    # Recuperar el historial desde la base de datos
    history = historyCollection.find().skip(skip).limit(limit)
    history_list = list(history)

    return jsonify({"history": history_list})