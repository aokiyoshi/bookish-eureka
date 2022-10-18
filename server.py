import socket
import sys

from requests import JSONDecodeError

import logs.server_log_config
from common import utils
from common.settings import *


class Server:

    logger = logging.getLogger('server')

    def validate(self, msg):
        self.logger.debug(f'Валидация сообщения {msg}')
        if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg \
                and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def init(self):
        utils.init_sygnal()

        if not 1023 < DEFAULT_PORT < 65536:
            self.logger.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                                 f'{DEFAULT_PORT}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', DEFAULT_PORT))
        self.socket.listen(1)
        self.logger.info(
            f'Сервер запущен. Адрес: localhost, порт {DEFAULT_PORT}')
        try:
            while True:
                self.client, addr = self.socket.accept()
                msg = utils.get_message(self.client)
                print(f'Клиент: ({addr[0]}:{addr[1]}), message: {msg}')
                self.logger.debug(
                    f'Клиент: ({addr[0]}:{addr[1]}), message: {msg}')
                self.logger.debug(
                    utils.send_message(self.client, self.validate(msg))
                )
                self.client.close()

        except JSONDecodeError as exception:
            self.logger.debug(f'Ошибка при валидации: {exception}')
        except Exception as exception:
            self.logger.debug(f'Неизвестная ошибка: {exception}')
        finally:
            self.socket.close()
            self.logger.info('Сервер остановлен')


if __name__ == "__main__":
    serv = Server()
    serv.init()
