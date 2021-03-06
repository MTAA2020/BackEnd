import json
import os
import base64
from datetime import datetime
from flask import Flask, make_response, request, jsonify, render_template, send_file
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from peewee import fn
import model

app = Flask(__name__, template_folder=os.getcwd().replace(os.sep, '/'))
app.config['JWT_SECRET_KEY'] = 'supersecret'
app.config['JWT_EXPIRATION_DELTA'] = False
jwt = JWTManager(app)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/teapot', methods=['GET'])
def teapot():
    return jsonify({'msg': 'Your teapot is preparing a coffee.'}), 418

# Funguje
@app.route('/register', methods=['POST'])
def registration():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    uname = request.json.get('username', str)
    passw = request.json.get('password', str)
    email = request.json.get('email', str)
    admin = request.json.get('admin', int)
    if admin == 1:
        admin = True
    else:
        admin = False

    try:
        userid = model.User.create(
            username=uname, passwordhash=passw, email=email, balance=0, admin=admin)
        if userid:
            return jsonify({'msg': 'Success'}), 201
    except:
        return jsonify({'msg': 'Username already taken'}), 500

# Funguje
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    uname = request.json.get('username', str)
    passw = request.json.get('password', str)

    if not uname:
        return jsonify({'msg': 'Missing username'}), 412
    if not passw:
        return jsonify({'msg': 'Missing password'}), 412

    try:
        user = model.User.select().where(model.User.username == uname).get()
        if uname == user.username and passw == user.passwordhash:
            access_token = create_access_token(identity=uname)
            return jsonify({'access_token': access_token, 'msg': 'Success', 'balance': user.balance, 'admin': user.admin}), 200
    except:
        return jsonify({'msg': 'Wrong username or password'}), 403
    return jsonify({'msg': 'Wrong details'}), 403

# Funguje
@app.route('/addAuthor', methods=['POST'])
@jwt_required
def addAuthor():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    author_name = request.json.get('name', str)
    author_about = request.json.get('about', str)
    print(type(author_name))
    print(type(author_about))
    current_user = get_jwt_identity()
    user = model.User.select().where(model.User.username == current_user).get()

    if user.admin is True:
        try:
            model.Author.create(name=author_name, about=author_about)
            return jsonify({'msg': 'success'}), 201
        except:
            return jsonify({'msg': 'Something went wrong'}), 400
    else:
        return jsonify({'msg': 'No permission'}), 403

# Funguje
@app.route('/addBook', methods=['POST'])
@jwt_required
def addBook():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    authorname = request.json.get('name', str)
    title = request.json.get('title', str)
    date = request.json.get('date', None)
    price = request.json.get('price', None)
    genres = request.json.get('genres', None)

    current_user = get_jwt_identity()
    user = model.User.select().where(model.User.username == current_user).get()

    if user.admin is True:
        try:
            auth = model.Author.select().where(model.Author.name == authorname).get()
            bookobj = model.Book.create(
                author=auth, title=title, published=date, rating=0, price=price, genres=genres)
            return jsonify({'msg': 'Success', "book_id": bookobj.id}), 201
        except:
            return jsonify({'msg': 'Something went wrong'}), 400
    else:
        return jsonify({'msg': 'No permission'}), 403


# Treba urobit
@app.route('/addpdf', methods=['POST'])
@jwt_required
def addPDF():
    subor = request.files['file']
    try:
        filename = os.getcwd().replace(os.sep, '/')+"/PDF/book_" + \
            str(request.form['book_id'])+".pdf"
        subor.save(filename)

        return jsonify({'msg': 'Success', "book_id": str(request.form['book_id'])}), 201
    except:
        return jsonify({'msg': 'Something went wrong'}), 400

# Treba urobit
@app.route('/addjpg', methods=['POST'])
@jwt_required
def addJPG():
    subor = request.files['file']
    try:
        filename = os.getcwd().replace(os.sep, '/')+"/JPG/book_" + \
            str(request.form['book_id'])+".jpg"
        subor.save(filename)
        return jsonify({'msg': 'Success', "book_id": str(request.form['book_id'])}), 201
    except:
        return jsonify({'msg': 'Something went wrong'}), 400


# Funguje
@app.route('/bookEdit', methods=['PUT'])
@jwt_required
def bookEdit():
    print(request)
    if not request.is_json:
        return jsonify({'msg': 'Wrong format'}), 400

    book_id = request.json.get('book_id', int)
    name = request.json.get('name', str)
    title = request.json.get('title', str)
    date = request.json.get('date', None)
    price = request.json.get('price', float)
    genres = request.json.get('genres', None)
    current_user = get_jwt_identity()
    user = model.User.select().where(model.User.username == current_user).get()
    authorobj = model.Author.select().where(model.Author.name == name).get()
    print(type(genres))
    print(genres)

    if user.admin is True:
        try:
            book = model.Book.select().where(model.Book.id == book_id).get()
            book.author_id = authorobj.id
            book.title = title
            book.published = date
            book.price = price
            book.genres = genres
            book.save()
            return jsonify({'msg': 'success'}), 200
        except:
            return jsonify({'msg': 'Something went wrong'}), 400
    else:
        return jsonify({'msg': 'No permission'}), 403


# Funguje
@app.route('/bookDelete', methods=['DELETE'])
@jwt_required
def bookDelete():
    bookid = request.args.get('book_id', None)
    print(bookid)
    current_user = get_jwt_identity()
    user = model.User.select().where(model.User.username == current_user).get()

    if user.admin is True:
        try:
            book = model.Book.select().where(model.Book.id == bookid).get()
            query = model.Purchase.delete().where(model.Purchase.book_id == book.id)
            query.execute()
            query = model.Review.delete().where(model.Review.book_id == book.id)
            query.execute()
            book.delete_instance()
            return jsonify({'msg': 'success'}), 200
        except:
            return jsonify({'msg': 'Something went wrong'}), 400
    else:
        return jsonify({'msg': 'No permission'}), 403

# Funguje
@app.route('/purchase', methods=['POST'])
@jwt_required
def purchase():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    book_id = request.json.get('book_id', int)
    date = datetime.now()

    current_user = get_jwt_identity()
    userobj = model.User.select().where(model.User.username == current_user).get()
    bookobj = model.Book.select().where(model.Book.id == book_id).get()

    if userobj.balance > bookobj.price:
        try:
            purchase = model.Purchase.select().where(model.Purchase.book_id == bookobj,
                                                     model.Purchase.user_id == userobj).get()
        except:
            try:
                purchase = model.Purchase.create(
                    user_id=userobj.id, book_id=bookobj, p_datetime=date)
                new_balance = userobj.balance-bookobj.price
                userobj.balance = new_balance
                userobj.save()
                if purchase:
                    return jsonify({'code': '1', 'msg': 'Success'}), 201
            except:
                return jsonify({'msg': "Couldn't create purchase"}), 500
    else:
        return jsonify({'code': '2', 'msg': 'No Credit'}), 406

    return jsonify({'code': '3', 'msg': 'You have already bought this book'}), 406


@app.route('/isbought', methods=['GET'])
@jwt_required
def isbought():
    current_user = get_jwt_identity()
    book_id = request.args.get('book_id')
    userobj = model.User.select().where(model.User.username == current_user).get()
    bookobj = model.Book.select().where(model.Book.id == book_id).get()

    try:
        tmp = model.Purchase.select().where(model.Purchase.book_id == bookobj,
                                            model.Purchase.user_id == userobj).get()
        return jsonify({'code': '1', 'msg': "You have this book"}), 200
    except:
        return jsonify({'code': '3', 'msg': 'You dont have this book'}), 200


# Funguje
@app.route('/deposit', methods=['POST'])
@jwt_required
def deposit():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    amount = request.json.get('amount', None)
    date = datetime.now()

    current_user = get_jwt_identity()
    userobj = model.User.select().where(model.User.username == current_user).get()
    currentbalance = float(userobj.balance)

    try:
        deposit = model.Deposit.create(
            user_id=userobj, amount=amount, d_datetime=date)
        new_balance = currentbalance+float(amount)
        userobj.balance = new_balance
        userobj.save()
        if deposit:
            return jsonify({'msg': 'Success', 'balance': new_balance}), 200
    except:
        return jsonify({'msg': 'Sorry something went wrong'}), 400

# Funguje
@app.route('/getBooks', methods=['GET'])
def getBooks():

    response = []
    try:
        books = model.Book.select().join(model.Author, on=(
            model.Author.id == model.Book.author)).order_by(fn.Random()).limit(5)
        for book in books:

            response.append({
                'id': book.id,
                'title': book.title,
                'author': book.author.name,
                'about': book.author.about,
                'published': book.published,
                'rating': book.rating,
                'price': book.price,
                'genres': book.genres,
            })
        if books:
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No more entries'}), 204
    except:
        return jsonify({'msg': 'No picture/book is present'}), 204
    return jsonify({'msg': 'Sorry something went wrong'}), 400

# Funguje
@app.route('/getBookReviews', methods=['GET'])
def getBookReviews():

    bookid = request.args.get('book_id', type=int)
    response = []
    strana = request.args.get('strana', type=int)
    try:
        reviews = model.Review.select().join(model.User, on=(model.User.id == model.Review.user_id)
                                             ).where(model.Review.book_id == bookid).paginate(strana, 10)

        if reviews:
            for review in reviews:
                response.append({
                    'user': review.user_id.username,
                    'time': review.time,
                    'rating': review.rating,
                    'comment': review.comment
                })
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No more reviews'}), 204
    except:
        return jsonify({'msg': "Sorry, can't find reviews"}), 404
    return jsonify({'msg': 'Sorry, something went wrong'}), 400

# Funguje
@app.route('/getMyBooks', methods=['GET'])
@jwt_required
def getMyBooks():

    current_user = get_jwt_identity()
    userid = model.User.get(model.User.username == current_user).id
    response = []
    strana = request.args.get('strana', type=int)
    try:
        myBooks = model.Book.select().join(model.Purchase).where(model.Purchase.book_id == model.Book.id).join(model.User).where(
            userid == model.Purchase.user_id).join(model.Author, on=(model.Author.id == model.Book.author)).paginate(strana, 10)

        if myBooks:
            for book in myBooks:

                response.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author.name,
                    'about': book.author.about,
                    'published': book.published,
                    'rating': book.rating,
                    'price': book.price,
                    'genres': book.genres,
                })
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No more entries'}), 204
    except:
        return jsonify({'msg': "Sorry, can't find your books"}), 404
    return jsonify({'msg': 'Sorry, something went wrong'}), 400


#Funguje    
@app.route('/getMyReview', methods=['GET'])
@jwt_required
def getmyreview():

    bookid = request.args.get('book_id',type=int)
    current_user = get_jwt_identity()
    try:
        review = model.Review.select().join(model.User, on=(model.User.id == model.Review.user_id)).where(model.Review.book_id == bookid,model.User.username == current_user).get()

        if review:
            return jsonify({'code': '1','rating': review.rating,'comment':review.comment}), 200
        else:
            return jsonify({'code': '3','msg': 'you have no review'}), 204
    except:
        return jsonify({'code': '3','msg': 'you have no review'}), 204

    return jsonify({'msg':'Sorry, something went wrong'}),400


#Funguje
@app.route('/getbalance', methods=['GET'])
@jwt_required
def getbalance():

    current_user = get_jwt_identity()

    try:
        userobj = model.User.select().where(model.User.username == current_user).get()
        currentbalance = float(userobj.balance)
        return jsonify({'balance': currentbalance}), 200
    except:
        return jsonify({'msg': 'Sorry something went wrong'}), 400


# Funguje
@app.route('/seePurchases', methods=['GET'])
@jwt_required
def seePurchases():
    strana = request.args.get('strana', type=int)
    current_user = get_jwt_identity()
    userobj = model.User.select().where(model.User.username == current_user).get()
    response = []
    try:
        purchases = model.Purchase.select().join(model.Book, on=(model.Book.id == model.Purchase.book_id)
                                                 ).where(model.Purchase.user_id == userobj).paginate(strana, 10)
        if purchases:
            for purchase in purchases:
                response.append({
                    'title': purchase.book_id.title,
                    'date': purchase.p_datetime,
                    'price': purchase.book_id.price
                })
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No purchases'}), 204
    except:
        return jsonify({'msg': 'Something went wrong'}), 400

# Funguje
@app.route('/addReview', methods=['PUT'])
@jwt_required
def addReview():
    if not request.is_json:
        return jsonify({'msg': 'Bad Request format'}), 400

    book_id = request.json.get('book_id', int)
    comment = request.json.get('comment', str)
    rating = request.json.get('rating', None)
    time = datetime.now()

    current_user = get_jwt_identity()
    userobj = model.User.select().where(model.User.username == current_user).get()
    bookobj = model.Book.select().where(model.Book.id == book_id).get()

    try:
        review = model.Review.select().where(model.Review.book_id == bookobj,
                                             model.Review.user_id == userobj).get()
        if rating != "0.0":
            review.rating = rating

        review.comment = comment
        review.time = time
        review.save()
        allreviews = model.Review.select().where(model.Review.book_id == bookobj)
        numberofreviews = 0
        totalrating = 0
        for rev in allreviews:
            numberofreviews += 1
            totalrating += rev.rating

        bookobj.rating = totalrating/numberofreviews
        bookobj.save()

        return jsonify({'msg': 'Success'}), 200
    except:
        try:
            newreview = model.Review.create(
                user_id=userobj, book_id=bookobj, time=time, comment=comment, rating=rating)
            return jsonify({'msg': 'Success'}), 200
        except:
            return jsonify({'msg': 'Something went wrong'}), 400


@app.route('/searchbook', methods=['GET'])
def searchbook():
    response = []
    hladanie = request.args.get('hladanie', str)
    try:
        books = model.Book.select().join(model.Author, on=(model.Author.id == model.Book.author)).where(
            (model.Book.title.iregexp(hladanie)) | (model.Author.name.iregexp(hladanie))).limit(40)

        for book in books:

            response.append({
                'id': book.id,
                'title': book.title,
                'author': book.author.name,
                'about': book.author.about,
                'published': str(book.published),
                'rating': book.rating,
                'price': book.price,
                'genres': book.genres,
            })
        if books:
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No more entries'}), 204
    except:
        return jsonify({'msg': 'No picture/book is present'}), 204
    return jsonify({'msg': 'Sorry something went wrong'}), 400


@app.route('/searchauthor', methods=['GET'])
def searchauthor():
    response = []
    hladanie = request.args.get('hladanie', str)
    try:
        authors = model.Author.select().where(model.Author.name.iregexp(hladanie))

        for author in authors:
            print(author.id)
            print(author.name)
            print(author.about)
            response.append({
                'id': author.id,
                'name': author.name,
                'about': author.about
            })
        if authors:
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No more entries'}), 204
    except:
        return jsonify({'msg': 'No picture/book is present'}), 204
    return jsonify({'msg': 'Sorry something went wrong'}), 400


@app.route('/getBookCategory', methods=['GET'])
def getBooksbycategory():

    response = []
    strana = request.args.get('strana', type=int)
    kategoria = request.args.get('kategoria', type=str)
    try:
        books = model.Book.select().where(model.Book.genres.contains(kategoria)).join(
            model.Author, on=(model.Author.id == model.Book.author)).paginate(strana, 10)

        for book in books:

            # if kategoria in book.genres:
            response.append({
                'id': book.id,
                'author': book.author.name,
                'title': book.title,
                'about': book.author.about,
                'published': book.published,
                'rating': book.rating,
                'price': book.price,
                'genres': book.genres,
            })

        if books:
            return jsonify(response), 200
        else:
            return jsonify({'msg': 'No more entries'}), 204
    except:
        return jsonify({'msg': 'No picture/book is present'}), 204
    return jsonify({'msg': 'Sorry something went wrong'}), 400


@app.route('/jpg', methods=['GET'])
def getjpg():

    book_id = request.args.get('book_id', int)

    filename = os.getcwd().replace(os.sep, '/')+"/JPG/book_"+str(book_id)+".jpg"
    try:
        file = open(filename, "rb")
    except:
        filename = os.getcwd().replace(os.sep, '/')+"/JPG/404.jpg"

    return send_file(filename)


@app.route('/pdf', methods=['GET'])
def getpdf():

    book_id = request.args.get('book_id', int)

    filename = os.getcwd().replace(os.sep, '/')+"/PDF/book_"+str(book_id)+".pdf"

    return send_file(filename, mimetype='text/pdf')
