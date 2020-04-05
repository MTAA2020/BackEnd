import json
import os
import base64
from flask import Flask, make_response, request, jsonify
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
@jwt_required
def addPDF():
    data=request.get_data()

    book_id=data[-8:]
    book_id=int.from_bytes( book_id, "big", signed=False )
    filename=os.getcwd().replace(os.sep, '/')+"/PDF/book_"+str(book_id)+".pdf"

#Treba urobit
@app.route('/addjpg', methods=['POST'])
@jwt_required
def addJPG():
    data=request.get_data()
    
    book_id=data[-8:]
    book_id=int.from_bytes( book_id, "big", signed=False )
    filename=os.getcwd().replace(os.sep, '/')+"/PDF/book_"+str(book_id)+".jpg"





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


#Funguje           
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
            purchase=model.Purchase.select().where(model.Purchase.book_id == bookobj, model.Purchase.user_id == userobj).get()
        except:
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
    
    return jsonify({'msg':'You have already bought this book'}), 406
            
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

#Funguje     
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

            #Treba osetrit pripad ked jpg sa nenajde na serveri
            filename=os.getcwd().replace(os.sep, '/')+"/JPG/book_"+str(book.id)+".jpg"
            with open(filename, "rb") as imageFile:
                jpg_base64 = base64.b64encode(imageFile.read())

            base64_string = jpg_base64.decode('ascii')

            response['knihy'].append({
                'id': book.id,
                'title': book.title,
                'cover' : base64_string
            })
        if books:
            return jsonify({'msg':'success','knihy':response}), 200
        else:
            return jsonify({'msg':'No more entries'}), 200
    except:
        return print("pepek")
    return jsonify({'msg':'coco'}), 500

#Funguje    
@app.route('/getBookReviews', methods=['GET'])
def getBookReviews():
    if not request.is_json:
        return jsonify({'msg': 'Wrong format'}), 400
    bookid = request.json.get('book_id',int)
    response = {}
    strana = request.json.get('strana',int)
    try:
        reviews = model.Review.select().where(model.Review.book_id == bookid).paginate(strana,10)
        response['pocet'] = len(reviews)
        response['reviews'] = []
        if reviews:
            for review in reviews:
                response['reviews'].append({
                    'time': review.time,
                    'rating': review.rating,
                    'comment': review.comment
                })
            return jsonify({'msg':'Success','reviews':response}), 200
        else:
            return jsonify({'msg':'No more reviews'}), 200  
    except:
        return jsonify({'msg':'wrong'}),400
    return jsonify({'msg':'coco'}),500

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

                #Treba osetrit pripad ked jpg sa nenajde na serveri
                filename=os.getcwd().replace(os.sep, '/')+"/JPG/book_"+str(book.id)+".jpg"
                with open(filename, "rb") as imageFile:
                    jpg_base64 = base64.b64encode(imageFile.read())
                base64_string = jpg_base64.decode('ascii')

                response['knihy'].append({
                    'id': book.id,
                    'title': book.title,
                    'cover': base64_string
                })
            return jsonify({'msg':'Success','knihy':response}), 200
        else:
            return jsonify({'msg':'No more entries'}), 200  
    except:
        return jsonify({'msg':'wrong'}),400
    return jsonify({'msg':'coco'}),500

#Treba upravit
@app.route('/getBookDetail', methods=['GET'])
def getBookDetail():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    book_id = request.json.get('book_id',int)
    user_id = request.json.get('user_id',int)
    #Mozno treba checknut ci user uz kupil tuto knihu,aby sme vedeli nastavit button na read alebo buy,alebo ked nebol login tak na login

    try:
        bookobj=model.Book.select().where(model.Book.id==book_id).get()
        return jsonify({'book_id': bookobj.id,
                        'author':bookobj.author,
                        'title':bookobj.title,
                        'published':bookobj.published,
                        'rating':bookobj.rating,
                        'price':bookobj.price,
                        'genres:':bookobj.genres}), 200
    except:
        return jsonify({'msg':'No purchases'}), 200


#Treba upravit
@app.route('/readBook', methods=['GET'])
@jwt_required
def readBook():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    
    book_id = request.json.get('book_id',None)

    current_user=get_jwt_identity()
    user = model.User.select().where(model.User.username == current_user).get()
    #Neviem ci treba najprv zistit ci user uz kupil knihu alebo nie,tlacitko na readbook aj tak bude dostupny iba vtedy.

    filename=os.getcwd().replace(os.sep, '/')+"/PDF/book_"+str(book_id)+".pdf"
    with open(filename, "rb") as pdfFile:
        jpg_base64 = base64.b64encode(pdfFile.read())

    base64_string = jpg_base64.decode('ascii')

    return jsonify({'pdf': base64_string}), 200

#Funguje           
@app.route('/seePurchases', methods=['GET'])
@jwt_required
def seePurchases():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400
    current_user = get_jwt_identity()
    userid = model.User.get(model.User.username == current_user).id
    response = {}
    try:
        purchasy = model.Purchase.select().where(model.Purchase.user_id == userid)
        if purchasy:
            response['pocet'] = len(purchasy)
            response['purchasy'] = []
            for purchas in purchasy:
                print(purchas.book_id)
                kniha = model.Book.select().where(model.Book.id == purchas.book_id).get()
                response['purchasy'].append({
                    'title':kniha.title,
                    'datum':purchas.p_datetime,
                    'cena':kniha.price
                })
            return jsonify({'msg':'success','knihy':response}), 200
        else:
            return jsonify({'msg':'No purchases'}), 200
    except:
        return jsonify({'msg':'Something went wrong'}), 400

#Funguje
@app.route('/addReview', methods=['POST'])
@jwt_required
def addReview():
    if not request.is_json:
            return jsonify({'msg': 'Wrong format'}), 400

    book_id = request.json.get('book_id',int)
    comment = request.json.get('comment',str)
    rating = request.json.get('rating',None)
    time = request.json.get('time',None)

    current_user=get_jwt_identity()
    userobj = model.User.select().where(model.User.username == current_user).get()
    bookobj = model.Book.select().where(model.Book.id == book_id).get()
    
    try:
        model.Review.select().where(model.Review.book_id == bookobj, model.Review.user_id == userobj).get()
    except:
        try:
            newreview=model.Review.create(user_id=userobj,book_id=bookobj,time=time,comment=comment,rating=rating)
            return jsonify({'msg': 'Success'}), 200
        except:
            return jsonify({'msg': 'Something went wrong'}) , 400
