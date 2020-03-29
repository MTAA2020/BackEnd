from flask import Flask, make_response, request, jsonify
import json
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import model

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'supersecret'
jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/register', methods=['POST'])
def registration():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    uname = request.json.get('username',None)
    passw = request.json.get('password', None)
    email = request.json.get('email',None)
    admin = request.json.get('admin',None)
    access_token = create_access_token(identity=uname)

    userid=model.User.create(username=uname,passwordhash=passw,token=access_token,email=email,balance=0,admin=admin)
    if userid:
        return jsonify({'msg': 'Success'}), 200
    

@app.route('/login', methods=['POST'])
def login():
        if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

        uname = request.json.get('username',None)
        passw = request.json.get('password', None)


        if not uname:
            return jsonify({'msg': 'Missing username'}) , 400
        if not passw:
            return jsonify({'msg': 'Missing password'}) , 400

        user = model.User.select().where(model.User.username == uname).get()
        if uname == user.username and passw == user.passwordhash:
            access_token = create_access_token(identity=uname)
            return jsonify(access_token=access_token), 200

        return jsonify({'msg': 'Wrong details'}) , 400


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
