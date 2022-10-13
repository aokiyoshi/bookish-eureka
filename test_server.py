import time
import unittest
from server import Server
from common.settings import *


class TestServerClass(unittest.TestCase):

    # Позитивный сценарий
    def test_validate(self):
        msg = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        serv = Server()
        self.assertEqual({RESPONSE: 200}, serv.validate(msg))

    # Неправильный action
    def test_validate_negative(self):
        msg = {
            ACTION: '111',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        serv = Server()
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, serv.validate(msg))

    # Нет action'а
    def test_validate_negative2(self):
        msg = {
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        serv = Server()
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, serv.validate(msg))

    # Неправильный пользователь
    def test_validate_negative3(self):
        msg = {
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest1'
            }
        }
        serv = Server()
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, serv.validate(msg))

    # Пустое время
    def test_validate_positive2(self):
        msg = {
            ACTION: PRESENCE,
            TIME: '',
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        serv = Server()
        self.assertEqual({RESPONSE: 200}, serv.validate(msg))

    

if __name__ == '__main__':
    unittest.main()