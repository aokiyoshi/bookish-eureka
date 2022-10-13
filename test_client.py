import time
import unittest
from client import Client
from common.settings import *


class TestClientClass(unittest.TestCase):

    # Проверка создания сообщения присуствия
    def test_create_presence(self):
        clnt = Client('localhost', 7777)
        self.assertEqual(
            {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: 'Guest'
                }
            },
            clnt.create_presence()
        )

    # Проверка обработки ответа 400
    def test_process_answer(self):
        clnt = Client('localhost', 7777)
        self.assertEqual(
            '400: Bad Request',
            clnt.process_answer({RESPONSE: 400, ERROR: 'Bad Request'})
        )
    
    # Проверка ответа 200
    def test_process_answer1(self):
        clnt = Client('localhost', 7777)
        self.assertEqual(
            '200: OK',
            clnt.process_answer({RESPONSE: 200})
        )
    
    # Проверка сценария, когда ответ это пустой словарь
    def test_process_answer2(self):
        clnt = Client('localhost', 7777)
        self.assertEqual(
            'Не удалось обработать ответ сервера',
            clnt.process_answer({})
        )

    # Проверка сценария, когда ответ это что-то другое
    def test_process_answer3(self):
        clnt = Client('localhost', 7777)
        self.assertEqual(
            'Не удалось обработать ответ сервера',
            clnt.process_answer('lorem')
        )
  

    

if __name__ == '__main__':
    unittest.main()