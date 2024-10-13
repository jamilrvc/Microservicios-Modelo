from flask import Flask, render_template, request, send_from_directory, abort
import requests
from random import sample
from pymongo import MongoClient
import os


app = Flask(__name__)

os.environ.get('GUNICORN_BIND')

#Funciones

def get_database(dbhost,dbname):
   client = MongoClient(dbhost)
   return client.get_database(dbname)


# Función para enviar el mensaje de "viewed" al microservicio de historial
def send_viewed_message_to_history(video_path):
    url = "http://history/viewed"
    headers = {
        "Content-Type": "application/json"
    }
    request_body = {
        "videoPath": video_path
    }

    try:
        # Enviar solicitud POST al microservicio
        response = requests.post(url, headers=headers, data=json.dumps(request_body))
        response.raise_for_status()
        print(f"Sent 'viewed' message for {video_path}")
    except requests.exceptions.RequestException as err:
        print(f"Failed to send 'viewed' message for {video_path}")
        print(err)



#path = "/video?path=SampleVideo_1280x720_1mb.mp4"
if os.environ.get('GUNICORN_BIND')==None:
    print("Hello world")



@app.route('/<path:path>',methods=['GET'])
def video_stream(path):
    if request.method == 'GET':
        try:
            video_response =  send_from_directory('static',  path)
            send_viewed_message_to_history(path)
            return video_response
        except FileNotFoundError:
            abort(404)