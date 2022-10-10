import json
import socket
import sys

from common.common_mixin import CommonMixin
from common.settings import *


class Server(CommonMixin):

    def validate(self, msg):
        if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg \
                and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', DEFAULT_PORT))
        self.socket.listen()
        print('Сервер запущен!')
        try:
            while True:
                self.client, addr = self.socket.accept()
                msg = self.get_message()
                print(f'Client: ({addr[0]}:{addr[1]}), message: {msg}')
                self.send_message(self.validate(msg))
                self.client.close()
        finally:
            self.socket.close()


if __name__ == "__main__":
    serv = Server()
    serv.run()
