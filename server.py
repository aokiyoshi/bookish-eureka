import asyncio

from common.settings import (ACTION, DEFAULT_IP_ADDRESS, DEFAULT_PORT,
                             MAX_PACKAGE_LENGTH, TIME)
from common.utils import deserialize, serialize
from descriptors import NonNegative
from logs import logger_decos, server_log_config
from handlers import MessageHandler
from metaclasses import ServerMeta


class Server(metaclass=ServerMeta):

    port = NonNegative('port')

    def __init__(self, host=None, port=None):
        self.host = host or DEFAULT_IP_ADDRESS
        self.port = port or DEFAULT_PORT
        self.handler = MessageHandler()

    def process_message(self, binary_data):
        data = deserialize(binary_data)
        try:
            return self.handler.__getattribute__(data[ACTION])(data)
        except AttributeError:
            return self.handler.error()
        except KeyError:
            print(f'Key Error for {data=}')
            return self.handler.error()

    async def handle_request(self, reader, writer):
        data = await reader.read(MAX_PACKAGE_LENGTH)
        if not data:
            print('collected empty data')
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
            print(f'Отключение по таймауту! До свидания, {addr!r}!')
        finally:
            addr = writer.get_extra_info('peername')
            print(f'{addr!r} отключился!')
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

    my_serv = Server()
    my_serv.start()
