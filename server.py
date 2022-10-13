import json
import socket
import sys

from common.settings import *
from common import utils


class Server:

    def validate(self, msg):
        print(msg)
        if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg \
                and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def init(self):
        utils.init_sygnal()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', DEFAULT_PORT))
        self.socket.listen(1)
        print('Сервер запущен!')
        try:
            while True:
            
                self.client, addr =  self.socket.accept()
                msg = utils.get_message(self.client)
                print(f'Client: ({addr[0]}:{addr[1]}), message: {msg}')
                utils.send_message(self.client, self.validate(msg))
                self.client.close()
        finally:
                self.socket.close()


if __name__ == "__main__":
    serv = Server()
    serv.init()
    print('Сервер остановлен')
