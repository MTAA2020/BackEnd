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

    try: 
        userid=model.User.create(username=uname,passwordhash=passw,email=email,balance=0,admin=admin)
        if userid:
            return jsonify({'msg': 'Success'}), 200
    except:
        return jsonify({'msg': 'Username already taken'}), 500
    

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

        try:
            user = model.User.select().where(model.User.username == uname).get()
            if uname == user.username and passw == user.passwordhash:
                access_token = create_access_token(identity=uname)
                return jsonify(access_token=access_token), 200
        except:
            return jsonify({'msg': 'Wrong username or password'})
        return jsonify({'msg': 'Wrong details'}) , 400
"""
@app.route('/addAuthor', methods=['POST'])
@jwt_required
def addAuthor():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

@app.route('/addBook', methods=['POST'])
@jwt_required
def addBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/addPDF', methods=['POST'])
@jwt_required
def addPDF():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/bookEdit', methods=['PUT'])
@jwt_required
def bookEdit():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/bookDelete', methods=['DELETE'])
@jwt_required
def bookDelete():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/purchase', methods=['POST'])
@jwt_required
def purchase():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/deposit', methods=['POST'])
@jwt_required
def deposit():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/getBooks', methods=['GET'])
def getBooks():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

@app.route('/getMyBooks', methods=['GET'])
def getMyBooks():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

@app.route('/getBookDetail', methods=['GET'])
def getBookDetail():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

@app.route('/readBook', methods=['GET'])
def readBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
            
@app.route('/seePurchases', methods=['GET'])
def seePurchases():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
"""