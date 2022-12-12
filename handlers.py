from common.settings import *
from common.utils import login_required, now
from models import *
import peewee
import secrets


class MessageHandler:

    def __init__(self, db=None):
        init_db()
        try:
            User.create_user(username='Server', password='admin')
            User.create_user(username='Guest', password='guest16565162223xdasdsa')
        except peewee.IntegrityError:
            pass

    def error(self):
        return {'ERROR': 405}

    def presence(self, data):
        ClientHistory.create(ip_addr=f'{data["addr"][0]}:{data["addr"][1]}')
        return {'OK': 200}

    def get_token(self, username):
        user = User.filter(username=username)

        if token:=Token.filter(user=user).first():
            return {'OK': 200, 'data': token.key}

        key = secrets.token_urlsafe(32)
        Token.create(user=user, key=key)

        return {'OK': 200, 'data': key}

    def login(self, data):
        username = data.get('username', '')
        password = data.get('password', '')
        if not User.filter(username=username):
            User.create_user(username=username, password=password)
        if User.check_password(username, password):
            return self.get_token(username)
        else:
            return {'OK': '200', 'messages': ['Wrong password!']}

    @login_required
    def get(self, data):
        user = User.filter(username=data.get('user', {}).get(ACCOUNT_NAME))
        sender = data.get('sender', None)
        result = []

        for message in Message.select().where((Message.reciever == user) | (Message.sender == user)).limit(100).order_by(Message.created_date):
            if message.sender.username == sender or message.reciever.username == sender:
                result.append(f'[{str(message.created_date)}] {message.sender.username}: {message.message}')
        return {'OK': 200, 'messages': result}

    @login_required
    def send(self, data):
        username = data.get('user').get(ACCOUNT_NAME)
        message=data.get('message')
        reciever=data.get('reciever')
        if data.get('reciever') is not None:
            Message.send_message(username, reciever, message)
        else:
            Message.send_message(username, 'Server', message)
        return {'OK': 201}

    @login_required
    def get_contacts(self, data):
        user = data.get('user', {}).get(ACCOUNT_NAME)
        result = []
        server = User.filter(username='Server').first()
        result.append({'user': server.username})
        if user=='Guest':
            return  {'OK': 200, 'data': result}
        for contact in Contact.filter(owner=User.filter(username=user)):
            result.append({
                'user': contact.client.username,
            })
        return {'OK': 200, 'data': result}

    @login_required
    def add_contact(self, data):
        username = data.get('user').get('account_name', '')
        contact = data.get('contact', '')

        if username == contact:
            Message.create_serv_msg(
                username, msg='Нельзя добавляеть самого себя!')
            return {'ERROR': 400}

        if Contact.select().where(
            (Contact.owner == User.filter(username=username)) & (
                Contact.client == User.filter(username=contact))
        ):
            Message.create_serv_msg(username, msg='Такой контакт существует!')
            return {'ERROR': 400}

        try:
            Contact.create(
                owner=User.filter(username=username),
                client=User.filter(username=contact)
            )
            Message.create_serv_msg(
                username, msg=f'Контакт {contact} добавлен!')

            return {'OK': 201}
        except peewee.IntegrityError:
            Message.create_serv_msg(
                username, msg=f'Ошибка при добавлении {contact}!')

            return {'ERROR': 400}

    def quit(self, data):
        user = data.get('user').get('account_name')
        Token.delete().where(Token.user == user).execute()
        return {'OK': 200}
