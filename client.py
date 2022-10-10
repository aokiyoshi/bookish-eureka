import json
import socket
import sys
import time

from common.common_mixin import CommonMixin
from common.settings import *


class Client(CommonMixin):
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = port

    def create_presence(self, account_name: str = 'Guest') -> dict:
        return {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }

    def process_answer(self, msg: dict) -> str:
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200 : OK'
            return f'400: {msg[ERROR]}'
        return 'Не удалось обработать ответ сервера'

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.addr, self.port))
        self.send_message(self.create_presence())
        print(self.process_answer(self.get_message()))
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
