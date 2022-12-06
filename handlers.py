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
        # Message.create(
        #     sender=User.filter(username='Server'),
        #     receiver=None,
        #     message=f'{user} присоеденился в чат',
        # )
        
        return {'OK': 200}

    def get(self, data):
        user = User.filter(username=data.get('user', {}).get(ACCOUNT_NAME))
        result = []
        for message in Message.select().where(Message.reciever==user):
            result.append({
                'id': message.id,
                'date': message.created_date.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                'user': message.sender.username,
                'message': message.message
            })
        Message.delete().where(Message.reciever==user).execute()
        return {'OK': 200, 'data': result}

    def send(self, data):

        for user in User.select():
            Message.create(
                sender=User.filter(username=data.get('user').get(ACCOUNT_NAME)),
                reciever=user,
                message=data.get('message')
            )
        
        return {'OK': 201}

    def get_contacts(self, data):
        user = data.get('user', {}).get(ACCOUNT_NAME)
        result = []
        for contact in Contact.select(owner=User.filter(username=user)):
            result.append({
                'user': contact.client.username,
            })
        return {'OK': 200, 'data': result}

    def add_contact(self, data):
        user = data.get('user').get('account_name')
        user_id = self.database.users.get_user_id_by_name(user)
        contact = data.get('contact')
        contact_id = self.database.users.get_user_id_by_name(contact)
        self.database.contacts.insert(user_id, contact_id)
        return {
            'OK': 200,
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

