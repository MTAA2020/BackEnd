from flask import Flask, make_response, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/login', methods=['POST'])
def login():
        if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

        username = request.json.get('username',None)
        password = request.json.get('password', None)
        if not username:
            return jsonify({'msg': 'Missing username'}) , 400
        if not password:
            return jsonify({'msg': 'Missing password'}) , 400
        return jsonify({'msg': 'Login sucessful'}) , 200
