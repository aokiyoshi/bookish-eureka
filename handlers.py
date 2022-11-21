import os
import time
import unittest
from common.settings import *
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
                    'info' : 'Server account'
                } 
            )
        except Exception:
            pass

    def presence(self, data):
        user = data.get('user').get('account_name')
        self.database.add_user( {'username': user, 'info' : ''} )
        self.database.messages.append(
            {
                'user': 'Server',
                'message': f'{user} присоеденился в чат',
                'date': data.get(TIME),
            }
        )
        return {'OK': 200}

    def get(self, data):
        user = data.get('user').get('account_name')
        msg_count = len(self.database.messages)
        last_read_msg_id = self.database.users.get_last_msg_idx(username=user)
        print(f'{last_read_msg_id=}')
        if last_read_msg_id == msg_count - 1:
            return {'OK': 200, 'data': []}

        response = self.database.messages.get_after(last_read_msg_id) # Здесь берется слайс, обрати внимение на двоеточие
        self.database.users.update_read_idx(msg_count - 1, user)
        return {'OK': 200, 'data': response}

    def send(self, data):
        self.database.messages.append(
            {
                'user': data.get('user').get('account_name'),
                'message': data.get('message'),
                'date': data.get(TIME),
            }
        )
        return {'OK': 201}

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
        print(test_handler.presence(dict))

    def test_get(self):
        
        test_handler = MessageHandler(db=Database('test.db'))
        test_handler.database.messages.append(
            {
                'user': 'Server',
                'message': 'some msg',
                'date': '',
            }
        )
        dict = {
            ACTION: 'get',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Server'
            }
        }
        print(f'{test_handler.get(dict)=}')

    def tearDown(self):
        os.remove(self.db)



if __name__ == "__main__":

    unittest.main()