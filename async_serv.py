import asyncio
import dis

from common.settings import ACTION, DEFAULT_PORT, MAX_PACKAGE_LENGTH, TIME
from common.utils import deserialize, serialize
from logs import logger_decos, server_log_config


class ServerMeta(type):
    """
    Метакласс, который проверяет, что у класса Server не должны быть
    использованы методы 'connect'
    """
    def __new__(cls, clsname, bases, clsdict):
        for _, value in clsdict.items():
            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.argval in ('connect',):
                        raise ValueError(
                            'Класс не должен содержать вызовов connect!')

        return type.__new__(cls, clsname, bases, clsdict)


class NonNegative:
    """Дескриптор на положительное значение порта"""

    def __init__(self, port):
        self.port = port

    def __get__(self, instance, owner):
        return instance.__dict__[self.port]

    def __set__(self, instance, value):
        if value < 0:
            print(
                f'Номер порта не должен быть отрицательным числом.',
                f'Выставлен порт {DEFAULT_PORT}'
            )
            instance.__dict__[self.port] = DEFAULT_PORT
        else:
            instance.__dict__[self.port] = value

    def __delete__(self, instance):
        del instance.__dict__[self.port]


class Database:
    messages = []
    users = {}


class MessageHandler:

    def __init__(self, database: Database):
        self.database = database

    def presence(self, data):
        user = data.get('user').get('account_name')
        self.database.users.setdefault(user, 0)
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
        last_unread_index = self.database.users.get(user)

        if last_unread_index == len(self.database.messages) - 1:
            return {'OK': 200, 'data': []}

        response = self.database.messages[last_unread_index + 1:]
        self.database.users[user] = len(self.database.messages) - 1
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


class Server(metaclass=ServerMeta):

    port = NonNegative('port')

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.handler = MessageHandler(Database())

    def process_message(self, binary_data):
        data = deserialize(binary_data)
        return self.handler.__getattribute__(data[ACTION])(data)

    async def handle_request(self, reader, writer):
        data = await reader.read(MAX_PACKAGE_LENGTH)
        if not data:
            return 1
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print(f"Received {message!r} from {addr!r}")
        response = self.process_message(data)
        print(f"Response to {addr!r}: {response}")
        writer.write(serialize(response))
        await writer.drain()
        return 0

    async def handle_conn(self, reader, writer):
        try:
            while True:
                result = await asyncio.wait_for(self.handle_request(reader, writer), 300)
                if result == 1:
                    break
        except ConnectionResetError:
            print('Connection lost!')
        except asyncio.exceptions.TimeoutError:
            addr = writer.get_extra_info('peername')
            print(f'Timeout exit! Bye, {addr!r}!')
        finally:
            print("Close the connection")
            writer.close()

    async def init(self):
        server = await asyncio.start_server(self.handle_conn, self.host, self.port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Сервер запущен на {addrs}')
        async with server:
            await server.serve_forever()

    def start(self):
        try:
            asyncio.run(self.init())
        except KeyboardInterrupt:
            print('Сервер отключен. До свидания!')


if __name__ == "__main__":

    my_serv = Server('127.0.0.1', 8888)
    my_serv.start()
