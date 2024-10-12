from flask import Flask, render_template, request, send_from_directory, abort
import requests
from random import sample
import os


app = Flask(__name__)

os.environ.get('GUNICORN_BIND')

#path = "/video?path=SampleVideo_1280x720_1mb.mp4"
if os.environ.get('GUNICORN_BIND')==None:
    print("Hello world")



@app.route('/<path:path>',methods=['GET'])
def video_stream(path):
    if request.method == 'GET':
        try:
            return  send_from_directory('static',  path)
        except FileNotFoundError:
            abort(404)