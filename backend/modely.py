from peewee import *
from playhouse.postgres_ext import *


database = PostgresqlDatabase('postgres', **{'user': 'postgres', 'password': 'postgres'})

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
    token = CharField(null=True)
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

