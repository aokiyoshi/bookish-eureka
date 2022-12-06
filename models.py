from peewee import *
import datetime


db = SqliteDatabase('db.db')


class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    created_date = DateTimeField(default=datetime.datetime.now)


class Message(BaseModel):
    sender = ForeignKeyField(User)
    reciever = ForeignKeyField(User, null=True, backref='messages')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)


class ClientHistory(BaseModel):
    ip_addr = TextField()
    login_date = DateTimeField(default=datetime.datetime.now)


class Contact(BaseModel):
    owner = ForeignKeyField(User, backref='contacts')
    client = ForeignKeyField(User)
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)


def init_db():
    db.connect()
    db.create_tables([User, Message, ClientHistory, Contact])
