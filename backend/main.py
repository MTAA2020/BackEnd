from flask import Flask, make_response, request, jsonify
import json
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import modely

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'supersecret'
jwt = JWTManager(app)

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
        if username != 'test' or password != 'test':
            return jsonify({"msg": "Bad username or password"}), 401

            # Identity can be any data that is json serializable
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

"""Takto by sme mali pouzivat token aby sa nestalo
ze po precitani nasej API dokumentacie nam niekto vymaze vsetky knihy.
https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage/?fbclid=IwAR3f3g7Xoenh9kRXIEGEBawMLF92MhioAz4WLW2jU12sMAPwO2k4XzZfRoE
https://jwt.io/introduction/?fbclid=IwAR0rh3GF8SvXcvQ0kFeLg6HhnIAqMRmhkjAJ3hSMt_AkeGEM_rK_khpJw7M"""

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

try:
    prihlaseny = modely.User.get(modely.User.username == 'user2')
    if prihlaseny.passwordhash == 'user1':
        print('si prihlaseny')
except:
    print('Debilko')
