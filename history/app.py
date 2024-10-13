from flask import Flask,jsonify, render_template, request, send_from_directory, abort
import requests
from random import sample
from pymongo import MongoClient
import os

# Variables de entorno
PORT = int(os.environ.get("PORT"))
DBHOST = os.environ.get("DBHOST")
DBNAME = os.environ.get("DBNAME")

# Inicializar la aplicación Flask
app = Flask(__name__)

# Conectar con el servidor de la base de datos
client = MongoClient(DBHOST)

# Obtener la base de datos
db = client[DBNAME]

# Obtener la colección de historial
historyCollection = db['history']

# Ruta POST para manejar el mensaje "viewed"
@app.route("/viewed", methods=['POST'])
def viewed():
    data = request.get_json()
    video_path = data.get("videoPath")

    if not video_path:
        return jsonify({"error": "videoPath is required"}), 400

    # Insertar el registro en la colección "history"
    historyCollection.insert_one({"videoPath": video_path})
    print(f"Added video {video_path} to history.")

    return '', 200  # Enviar una respuesta HTTP 200 OK

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