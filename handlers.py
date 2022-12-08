from common.settings import *
from common.utils import now
from models import *
import peewee


class MessageHandler:

    def __init__(self, db=None):
        init_db()
        try:
            User.create(username='Server')
        except peewee.IntegrityError:
            pass

    def error(self):
        return {'ERROR': 405}

    def presence(self, data):
        user = data.get('user').get('account_name')
        try:
            User.create(username=user)
        except peewee.IntegrityError:
            pass
        
        return {'OK': 200}

    def get(self, data):
        user = User.filter(username=data.get('user', {}).get(ACCOUNT_NAME))
        server_user = User.filter(username='Server')
        sender = data.get('sender', None)
        result = []
        
        for message in Message.select().where((Message.reciever == user) | (Message.sender == user)).limit(100).order_by(Message.created_date):
            print(message.message)
            if message.sender.username == sender or message.reciever.username == sender:
                result.append({
                    'id': message.id,
                    'date': str(message.created_date),
                    'user': message.sender.username,
                    'message': message.message
                })

        return {'OK': 200, 'data': result, 'next': True}


    def send(self, data):
        username=data.get('user').get(ACCOUNT_NAME)
        
        if data.get('reciever') is not None:
            Message.create(
                sender=User.filter(username=username),
                reciever=User.filter(username=data.get('reciever')),
                message=data.get('message')
            )
        else:
            Message.create(
                sender=User.filter(username=username),
                reciever=User.filter(username='Server'),
                message=data.get('message')
            )
        return {'OK': 201}

    def get_contacts(self, data):
        user = data.get('user', {}).get(ACCOUNT_NAME)
        result = []
        for contact in Contact.filter(owner=User.filter(username=user)):
            result.append({
                'user': contact.client.username,
            })
        return {'OK': 200, 'data': result}

    def add_contact(self, data):
        username = data.get('user').get('account_name', '')
        contact = data.get('contact', '')
        date = data.get('time')
        if username == contact:
            Message.create(
                sender=User.filter(username=username),
                reciever=User.filter(username='Server'),
                message='Нельзя добавляеть самого себя!'
            )
            return {
                'ERROR': 400,
            }
        if Contact.select().where((Contact.owner == User.filter(username=username)) & (Contact.client == User.filter(username=contact))):
            Message.create(
                sender=User.filter(username='Server'),
                reciever=User.filter(username=username),
                message='Такой контакт существует!'
            )
            return {
                'ERROR': 400,
            }
        try:
            Contact.create(
                owner=User.filter(username=username),
                client=User.filter(username=contact)
            )
            Message.create(
                sender=User.filter(username=username),
                reciever=User.filter(username='Server'),
                message=data.get(f'Контакт {contact} добавлен!')
            )
            return {
                'OK': 201,
            }
        except peewee.IntegrityError:
            Message.create(
                sender=User.filter(username='Server'),
                reciever=User.filter(username=username),
                message=f'Ошибка при добавлении {contact}!'
            )
            return {
                'ERROR': 400,
            }


    def quit(self, data):
        user = data.get('user').get('account_name')
        self.database.messages.append(
            {
                'user': 'Server',
                'message': f'{user} отключился',
                'date': data.get(TIME),
            }
        )
        return {'OK': 200}

