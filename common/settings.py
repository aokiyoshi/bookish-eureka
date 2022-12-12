"""Константы"""
import logging



# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777

# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Максимальная очередь подключений
MAX_CONNECTIONS = 5

# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 8096

# Кодировка проекта
ENCODING = 'utf-8'

# Уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# База данных
DATABASE_NAME = 'database.db'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
SEND = 'send'
RECIEVE = 'recieve'
MESSAGE = 'message'
BYE = 'bye'
QUIT = 'quit'
