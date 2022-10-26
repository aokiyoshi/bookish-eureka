import sys
import select
from requests import JSONDecodeError

import logs.server_log_config
from common import utils
from common.settings import *
from logs import server_log_config, logger_decos

from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from socket import socket as socket_


class Server:

    logger = logging.getLogger('server')
    

    @logger_decos.log
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

        with socket_(AF_INET, SOCK_STREAM) as server_sock: 
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            server_sock.bind(('', DEFAULT_PORT))
            server_sock.listen(5)
            server_sock.settimeout(5)
            self.logger.info(
                f'Сервер запущен. Адрес: localhost, порт {DEFAULT_PORT}')
            client_sock_sockets = []

            while True:
                try:
                    client_sock, addr = server_sock.accept()
                except JSONDecodeError as exception:
                    self.logger.debug(f'Ошибка при валидации: {exception}')
                except Exception as exception:
                    self.logger.debug(f'Неизвестная ошибка: {exception}')
                else:
                    client_sock_sockets.append(client_sock)
                finally:
                    for socket in client_sock_sockets:
                        cl_read = []
                        print(client_sock_sockets)
                        cl_read, _, _ = select.select(client_sock_sockets, client_sock_sockets, client_sock_sockets, 0)
                        if socket in cl_read:
                            msg = utils.get_message(socket)
                            print(f'Клиент: ({addr[0]}:{addr[1]}), message: {msg}')
                            self.logger.debug(
                                f'Клиент: ({addr[0]}:{addr[1]}), message: {msg}')
                            self.logger.debug(
                                utils.send_message(socket, self.validate(msg))
                            )
                

if __name__ == "__main__":
    serv = Server()
    serv.init()
