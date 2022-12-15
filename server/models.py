import datetime
import hashlib
import uuid

from peewee import (CharField, DateTimeField, ForeignKeyField, Model,
                    SqliteDatabase, TextField)

db = SqliteDatabase('db.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField(null=False)
    salt = CharField(null=False)
    created_date = DateTimeField(default=datetime.datetime.now)

    def create_user(username, password):
        _salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(
            (password + _salt).encode()).hexdigest()
        User.create(username=username, password=hashed_password, salt=_salt)

    def check_password(username, password):
        user = User.filter(username=username).first()
        _salt = user.salt
        hashed_password = hashlib.sha512(
            (password + _salt).encode()).hexdigest()
        return user.password == hashed_password


class Message(BaseModel):
    sender = ForeignKeyField(User)
    reciever = ForeignKeyField(User, null=True, backref='messages')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)

    def create_serv_msg(username, msg):
        Message.create(
            sender=User.filter(username=username),
            reciever=User.filter(username='Server'),
            message=msg
        )

    def send_message(sender_username, reciever_username, message):
        Message.create(
            sender=User.filter(username=sender_username),
            reciever=User.filter(username=reciever_username),
            message=message
        )


class ClientHistory(BaseModel):
    ip_addr = TextField()
    login_date = DateTimeField(default=datetime.datetime.now)


class Contact(BaseModel):
    owner = ForeignKeyField(User, backref='contacts')
    client = ForeignKeyField(User)
    created_date = DateTimeField(default=datetime.datetime.now)


class Token(BaseModel):
    user = ForeignKeyField(User)
    key = CharField(null=False)

    def check_given_token(token, username):
        user = User.filter(username=username).first()
        stored_token = Token.filter(user=user).first()
        if not stored_token:
            return False
        return stored_token.key == token


def init_db():
    db.connect()
    db.create_tables([User, Message, ClientHistory, Contact, Token])
