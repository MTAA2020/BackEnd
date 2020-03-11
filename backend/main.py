from flask import Flask, make_response, request, jsonify
import json
from peewee import *
from playhouse.postgres_ext import *
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

database = PostgresqlDatabase('postgres', **{'host': '127.0.0.1', 'user': 'postgres', 'password': 'postgres'})
app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'supersecret'
jwt = JWTManager(app)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Author(BaseModel):
    about = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'author'

class Book(BaseModel):
    author = ForeignKeyField(column_name='author_id', field='id', model=Author, null=True)
    genres = ArrayField(field_class=CharField, null=True)
    price = DoubleField(null=True)
    published = DateField(null=True)
    rating = DoubleField(null=True)
    title = CharField(null=True)

    class Meta:
        table_name = 'book'

class User(BaseModel):
    admin = BooleanField(null=True)
    balance = DoubleField(null=True)
    email = CharField(null=True)
    passwordhash = CharField(null=True)
    username = CharField(null=True)

    class Meta:
        table_name = 'user'

class Deposit(BaseModel):
    amount = DoubleField(null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'deposit'

class Jpg(BaseModel):
    book = ForeignKeyField(column_name='book_id', field='id', model=Book, null=True)
    jpg = BlobField(null=True)
    jpgname = CharField(null=True)

    class Meta:
        table_name = 'jpg'
        primary_key = False

class Pdf(BaseModel):
    book = ForeignKeyField(column_name='book_id', field='id', model=Book, null=True)
    pdf = BlobField(null=True)
    pdfname = CharField(null=True)

    class Meta:
        table_name = 'pdf'
        primary_key = False

class Purchase(BaseModel):
    book = ForeignKeyField(column_name='book_id', field='id', model=Book, null=True)
    p_datetime = DateField(null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'purchase'

class Review(BaseModel):
    book = ForeignKeyField(column_name='book_id', field='id', model=Book, null=True)
    comment = TextField(null=True)
    rating = DoubleField(null=True)
    time = DateField(null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'review'

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
