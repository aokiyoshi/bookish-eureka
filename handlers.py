import datetime
import os
import time
import unittest
from common.settings import *
from common.utils import now
from database import Database


class MessageHandler:

    def __init__(self, db=None):
        if db is None:
            self.database = Database()
        else:
            self.database = db
        try:
            self.database.add_user(
                {
                    'id': 1,
                    'username': 'Server',
                    'info': 'Server account',
                    'msg_read_date': 0
                }
            )
        except Exception:
            pass

    def error(self):
        return {'ERROR': 405}

    def presence(self, data):
        user = data.get('user').get('account_name')
        self.database.add_user(
            {'username': user, 'info': '', 'msg_read_date': 0})
        self.database.messages.append(
            {
                'user': 'Server',
                'message': f'{user} присоеденился в чат',
                'date': data.get(TIME),
            }
        )
        return {'OK': 200}

    def get(self, data):
        user = data.get('user', {}).get(ACCOUNT_NAME)
        date = self.database.users.get_msgs_read_date(user)
        messages = self.database.messages.get_after(date)[:10]
        if messages:
            self.database.users.update_msg_read_datex(
                messages[-1].get(date, now()), user)
            return {'OK': 200, 'data': messages}
        return {'OK': 200, 'data': []}

    def send(self, data):
        self.database.messages.append(
            {
                'user': data.get('user').get(ACCOUNT_NAME),
                'message': data.get('message'),
                'date': data.get(TIME),
            }
        )
        return {'OK': 201}

    def get_contacts(self, data):
        user = data.get('user').get('account_name')
        user_id = self.database.users.get_user_id_by_name(user)
        data = [
            {
                'user': 'Server',
                'message': self.database.users.get_by_id(user.get('client_id', None)).get('username', ''),
                'date': now(),
            }
            for user in self.database.contacts.select(owner_id=user_id)
        ]
        return {
            'OK': 200,
            'data': data
        }

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


class TestMessageHandler(unittest.TestCase):

    def setUp(self):
        self.db = 'test.db'

    def test_presence(self):
        test_handler = MessageHandler(db=Database('test.db'))
        dict = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'John'
            }
        }

        assert test_handler.presence(data=dict).get("OK") == 200

    def test_get(self):

        test_handler = MessageHandler(db=Database('test.db'))

        test_handler.database.messages.append(
            {
                'user': 'Server',
                'message': 'some msg',
                'date': '',
            }
        )

        test_handler.database.users.insert(username='test', info='')
        dict = {
            ACTION: 'get',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'test'
            }
        }
        assert test_handler.get(data=dict).get("OK") == 200

    def test_get_contacts(self):
        """
        Взять контакты
        """
        test_handler = MessageHandler(db=Database('test.db'))
        test_handler.database.users.insert(username='test')
        dict = {
            ACTION: 'get_contacts',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'test'
            }
        }
        assert test_handler.get_contacts(data=dict).get("OK") == 200

    def test_add_contact(self):
        test_handler = MessageHandler(db=Database('test.db'))
        test_handler.database.users.insert(username='test')
        dict = {
            ACTION: 'add_contact',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'test'
            },
            'contact': 'test'
        }
        assert test_handler.add_contact(dict).get("OK") == 200

    def tearDown(self):
        os.remove(self.db)


if __name__ == "__main__":

    unittest.main()
