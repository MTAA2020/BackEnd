from flask import Flask, make_response, request
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'