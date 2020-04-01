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
            return jsonify({'msg': 'Wrong username or password'}), 400
        return jsonify({'msg': 'Wrong details'}) , 400


@app.route('/addAuthor', methods=['POST'])
@jwt_required
def addAuthor():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    author_name = request.json.get('name',None)
    author_about = request.json.get('about',None)

    current_user=get_jwt_identity()
    
    user = model.User.select().where(model.User.username == current_user).get()

    if user.admin is True:
        try:
            model.Author.create(name=author_name,about=author_about)
            return jsonify({'msg': 'success'}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400


@app.route('/addBook', methods=['POST'])
@jwt_required
def addBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    authorname = request.json.get('name',None)
    title = request.json.get('title',None)
    date = request.json.get('date',None)
    price = request.json.get('price',None)
    genres = request.json.get('genres',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()

    
    if user.admin is True:
        try:
            auth = model.Author.select().where(model.Author.name == authorname).get()
            model.Book.create(author=auth,title=title,published=date,rating=0,price=price,genres=genres)
            return jsonify({'msg': 'success'}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400

            
@app.route('/addPDF', methods=['POST'])
@jwt_required
def addPDF():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    bookid = request.json.get('book_id',None)
    pdfname = request.json.get('pdfname',None)
    pdf = request.json.get('pdf',None)
    token = request.json.get('token',None)
    userid = request.json.get('user',None)
            
@app.route('/bookEdit', methods=['PUT'])
@jwt_required
def bookEdit():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    name = request.json.get('name',None)
    title = request.json.get('title',None)
    date = request.json.get('date',None)
    price = request.json.get('price',None)
    genres = request.json.get('genres',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()

    
    if user.admin is True:
        try:
            book=model.Book.select().where(model.Book.title == title).get()
            book.name=name
            book.title=title
            book.date=date
            book.price=price
            book.genres=genres
            book.save()
            return jsonify({'msg': 'success'}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400


            
@app.route('/bookDelete', methods=['DELETE'])
@jwt_required
def bookDelete():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    bookid = request.json.get('book_id',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()

    
    if user.admin is True:
        try:
            book = model.Book.select().where(model.Book.id == bookid).get()
            book.delete_instance()
            return jsonify({'msg': 'success'}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400

            
@app.route('/purchase', methods=['POST'])
#@jwt_required
def purchase():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    userid = request.json.get('user',None)
    book = request.json.get('book',None)
    date = request.json.get('date',None)
    
    try: 
        purchase = model.Purchase.create(user_id=userid,book_id=book,p_datetime=date)
        if purchase:
            return jsonify({'msg': 'Success'}), 200
    except:
        return jsonify({'msg': "Couldn't create purchase"}), 500
            
@app.route('/deposit', methods=['POST'])
@jwt_required
def deposit():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    userid = request.json.get('user',None)
    amount = request.json.get('amount',None)
    date = request.json.get('date',None)
    
    try:
        deposit = model.Deposit.create(user_id=userid,amount=amount,d_datetime=date)
        if deposit:
            return jsonify({'msg':'Success'}), 200
    except:
        return jsonify({'msg':'Sorry something went wrong'}), 400
            
@app.route('/getBooks', methods=['GET'])
def getBooks():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    response = {}
    try:
        books = model.Book.select()
        response['pocet'] = len(books)
        response['knihy'] = []
        for book in books:
            cover = model.Jpg.get(model.Jpg.book_id == book.id)
            response['knihy'].append({
                'id': book.id,
                'title': book.title,
                'cover': (cover.jpg).tobytes().decode('utf8').replace("'",'"')
            })
        if books:
            return jsonify({'msg':'success','knihy':response}), 200
    except:
        return print("pepek")
    


@app.route('/getMyBooks', methods=['GET'])
def getMyBooks():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    userid = request.json.get('user_id',None)
    response = {}
    try:
        myBooks = model.Book.select().join(model.Purchase).where(model.Purchase.book_id == model.Book.id).join(model.User).where(userid == model.Purchase.user_id)
        response['pocet'] = len(myBooks)
        response['knihy'] = []
        if myBooks:
            for book in myBooks:
                cover = model.Jpg.get(model.Jpg.book_id == book.id)
                response['knihy'].append({
                    'id': book.id,
                    'title': book.title,
                    'cover': (cover.jpg).tobytes().decode('utf8').replace("'",'"')
                })
            return jsonify({'msg':'Success','knihy':response}), 200
        
    except:
        return jsonify({'msg':'wrong'}),400

@app.route('/getBookDetail', methods=['GET'])
def getBookDetail():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    bookid= request.json.get('book_id',None)







@app.route('/readBook', methods=['GET'])
@jwt_required
def readBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    bookid = request.json.get('book_id',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()

    mybook=model.Book.select().join(model.Purchase).where(model.Purchase.book_id == bookid).join(model.User).where(user == model.Purchase.user_id)


            
@app.route('/seePurchases', methods=['GET'])
def seePurchases():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    userid = request.json.get('user',None)
    token = request.json.get('token',None)
    response = {}
    try:
        purchasy = model.Purchase.select(model.Purchase.user_id == userid)
        response['pocet'] = len(purchasy)
        response['purchasy'] = []
        for purchas in purchasy:
            kniha = model.Book.select(model.Book.id == purchas.book_id)
            response['purchas'].append({
                'title':kniha.title,
                'datum':purchas.p_datetime,
                'cena':kniha.price
            })
        if purchasy:
            return jsonify({'msg':success}), 200
    except:
        return jsonify({'msg':'Something went wrong'}), 400

