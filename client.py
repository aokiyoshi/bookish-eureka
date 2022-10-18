import socket
import sys
import time

import logs.client_log_config
from common import utils
from common.settings import *


class Client:

    logger = logging.getLogger('client')

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def create_presence(self, account_name: str = 'Guest'):
        self.logger.debug(
            f'Создание presence-сообщения. Аккаунт: {account_name}')
        return {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }

    def process_answer(self, msg: dict) -> str:
        self.logger.debug(f'Обработка ответа: {msg}')
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200: OK'
            return f'400: {msg[ERROR]}'
        return 'Не удалось обработать ответ сервера'

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug(f'Попытка подключиться на {self.addr}: {self.port}')
        self.client.connect((self.addr, self.port))
        self.logger.debug(
            utils.send_message(self.client, self.create_presence())
        )
        print(self.process_answer(utils.get_message(self.client)))
        self.client.close()


if __name__ == '__main__':
    args = sys.argv

    server_address = DEFAULT_IP_ADDRESS
    server_port = DEFAULT_PORT

    if len(args) > 1:
        server_address = args[1]

    if len(args) > 2:
        server_port = args[2]

    clnt = Client(server_address, int(server_port))
    clnt.run()
