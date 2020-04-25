from peewee import *
from playhouse.postgres_ext import *

database = PostgresqlDatabase('postgres', **{'user': 'postgres', 'password': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Author(BaseModel):
    id = IdentityField(null=True,unique=True)
    name = CharField(null=True,unique=True)
    about = CharField(null=True)

    class Meta:
        table_name = 'author'

class Book(BaseModel):
    id = IdentityField(null=True,unique=True)
    author = ForeignKeyField(column_name='author_id', field='id', model=Author, null=True)
    title = CharField(null=True)
    published = DateField(null=True)
    rating = DoubleField(null=True)
    price = DoubleField(null=True)
    genres = ArrayField(field_class=CharField, null=True)

    class Meta:
        table_name = 'book'

class User(BaseModel):
    id = IdentityField(null=True,unique=True)
    username = CharField(null=True,unique=True)
    passwordhash = CharField(null=True)
    email = CharField(null=True,unique=True)
    balance = DoubleField(null=True)
    admin = BooleanField(null=True)

    class Meta:
        table_name = 'user'

class Deposit(BaseModel):
    id = IdentityField(null=True,unique=True)
    amount = DoubleField(null=True)
    user_id = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)
    d_datetime=DateTimeField(null=True)

    class Meta:
        table_name = 'deposit'


class Purchase(BaseModel):
    id = IdentityField(null=True,unique=True)
    book_id = ForeignKeyField(column_name='book_id', field='id', model=Book, null=True)
    p_datetime = DateTimeField(null=True)
    user_id = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'purchase'

class Review(BaseModel):
    id = IdentityField(null=True,unique=True)
    book_id = ForeignKeyField(column_name='book_id', field='id', model=Book, null=True)
    user_id = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)
    time = DateTimeField(null=True)
    rating = DoubleField()
    comment = TextField()

    class Meta:
        table_name = 'review'