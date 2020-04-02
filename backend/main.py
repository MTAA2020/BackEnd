from flask import Flask, make_response, request, jsonify
import json
import os
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

#Funguje
@app.route('/register', methods=['POST'])
def registration():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    uname = request.json.get('username',str)
    passw = request.json.get('password', str)
    email = request.json.get('email',str)
    admin = request.json.get('admin',bool)

    try: 
        userid=model.User.create(username=uname,passwordhash=passw,email=email,balance=0,admin=admin)
        if userid:
            return jsonify({'msg': 'Success'}), 200
    except:
        return jsonify({'msg': 'Username already taken'}), 500
    
#Funguje
@app.route('/login', methods=['POST'])
def login():
        if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

        uname = request.json.get('username',str)
        passw = request.json.get('password', str)


        if not uname:
            return jsonify({'msg': 'Missing username'}) , 400
        if not passw:
            return jsonify({'msg': 'Missing password'}) , 400

        try:
            user = model.User.select().where(model.User.username == uname).get()
            if uname == user.username and passw == user.passwordhash:
                access_token = create_access_token(identity=uname)
                return jsonify({'access_token':access_token,'msg':'Success','balance':user.balance}), 200
        except:
            return jsonify({'msg': 'Wrong username or password'}), 400
        return jsonify({'msg': 'Wrong details'}) , 400

#Funguje
@app.route('/addAuthor', methods=['POST'])
@jwt_required
def addAuthor():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    author_name = request.json.get('name',str)
    author_about = request.json.get('about',str)

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

#Funguje
@app.route('/addBook', methods=['POST'])
@jwt_required
def addBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    authorname = request.json.get('name',str)
    title = request.json.get('title',str)
    date = request.json.get('date',None)
    price = request.json.get('price',None)
    genres = request.json.get('genres',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()
    
    if user.admin is True:
        try:
            auth = model.Author.select().where(model.Author.name == authorname).get()
            bookobj = model.Book.create(author=auth,title=title,published=date,rating=0,price=price,genres=genres)
            return jsonify({'msg': 'Success',"book_id" : str(bookobj.id)}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400


#Treba urobit
@app.route('/addpdf', methods=['POST'])
#@jwt_required
def addPDF():
    currentDirectory = os.getcwd().replace(os.sep, '/')+"/PDF/"
    data=request.get_data()

#Treba urobit
@app.route('/addjpg', methods=['POST'])
@jwt_required
def addJPG():
    currentDirectory = os.getcwd().replace(os.sep, '/')+"/JPG/"
    data=request.get_data()



#Funguje            
@app.route('/bookEdit', methods=['PUT'])
@jwt_required
def bookEdit():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    book_id = request.json.get('book_id',int)
    name = request.json.get('name',str)
    title = request.json.get('title',str)
    date = request.json.get('date',None)
    price = request.json.get('price',float)
    genres = request.json.get('genres',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()

    authorobj=model.Author.select().where(model.Author.name == name).get()

    if user.admin is True:
        try:
            book=model.Book.select().where(model.Book.id == book_id).get()
            book.name=authorobj
            book.title=title
            book.published=date
            book.price=price
            book.genres=genres
            book.save()
            return jsonify({'msg': 'success'}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400


#Treba vyskusat            
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
            query = model.Purchase.delete().where(model.Purchase.book_id == book.id)
            query.execute()
            query = model.Review.delete().where(model.Review.book_id == book.id)
            query.execute()
            book.delete_instance()
            return jsonify({'msg': 'success'}) , 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
    else:
        return jsonify({'msg': 'No permission'}) , 400

#Funguje            
@app.route('/purchase', methods=['POST'])
@jwt_required
def purchase():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    book_id = request.json.get('book_id',None)
    date = request.json.get('date',None)

    current_user=get_jwt_identity()

    userobj = model.User.select().where(model.User.username == current_user).get()
    bookobj = model.Book.select().where(model.Book.id == book_id).get()

    if userobj.balance > bookobj.price:
        try: 
            purchase = model.Purchase.create(user_id=userobj.id,book_id=bookobj,p_datetime=date)
            new_balance=userobj.balance-bookobj.price
            userobj.balance=new_balance
            userobj.save()
            if purchase:
                return jsonify({'msg': 'Success'}), 200
        except:
            return jsonify({'msg': "Couldn't create purchase"}), 500
    else:
        return jsonify({'msg':'Not enough credit'}), 406
            
#Funguje
@app.route('/deposit', methods=['POST'])
@jwt_required
def deposit():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    amount = request.json.get('amount',None)
    date = request.json.get('date',None)

    current_user=get_jwt_identity()

    userobj = model.User.select().where(model.User.username == current_user).get()
    currentbalance=float(userobj.balance)

    try:
        deposit = model.Deposit.create(user_id=userobj,amount=amount,d_datetime=date)
        new_balance=currentbalance+float(amount)
        userobj.balance=new_balance
        userobj.save()
        if deposit:
            return jsonify({'msg':'Success'}), 200
    except:
        return jsonify({'msg':'Sorry something went wrong'}), 400

#Funguje - este dorobit COVER      
@app.route('/getBooks', methods=['GET'])
def getBooks():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    response = {}
    strana = request.json.get('strana',int)
    try:
        books = model.Book.select().paginate(strana,10)
        response['pocet'] = len(books)
        response['knihy'] = []
        for book in books:
            response['knihy'].append({
                'id': book.id,
                'title': book.title,
 #               'cover': TODO
            })
        if books:
            return jsonify({'msg':'success','knihy':response}), 200
        else:
            return jsonify({'msg':'No more entries'}), 200
    except:
        return print("pepek")
    

#Funguje
@app.route('/getMyBooks', methods=['GET'])
@jwt_required
def getMyBooks():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    current_user = get_jwt_identity()
    userid = model.User.get(model.User.username == current_user).id
    response = {}
    strana = request.json.get('strana',int)
    try:
        myBooks = model.Book.select().join(model.Purchase).where(model.Purchase.book_id == model.Book.id).join(model.User).where(userid == model.Purchase.user_id).paginate(strana,10)
        response['pocet'] = len(myBooks)
        response['knihy'] = []
        if myBooks:
            for book in myBooks:
                response['knihy'].append({
                    'id': book.id,
                    'title': book.title,
 #                   'cover': TODO,
                })
            return jsonify({'msg':'Success','knihy':response}), 200
        else:
            return jsonify({'msg':'No more entries'}), 200  
    except:
        return jsonify({'msg':'wrong'}),400
    return jsonify({'msg':'coco'}),500



#Treba urobit
@app.route('/getBookDetail', methods=['GET'])
def getBookDetail():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    bookid= request.json.get('book_id',None)




#Treba urobit
@app.route('/readBook', methods=['GET'])
@jwt_required
def readBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    bookid = request.json.get('book_id',None)

    current_user=get_jwt_identity()

    user = model.User.select().where(model.User.username == current_user).get()

    mybook=model.Book.select().join(model.Purchase).where(model.Purchase.book_id == bookid).join(model.User).where(user == model.Purchase.user_id)


#Este nefunguje           
@app.route('/seePurchases', methods=['GET'])
@jwt_required
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


#Treba urobit
@app.route('/getBookDetail', methods=['GET'])
@jwt_required
def addReview():
    pass
