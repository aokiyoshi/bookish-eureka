import asyncio
import datetime
import time

from common.settings import *
from common.utils import deserialize, serialize
from logs import client_log_config, logger_decos
import sys


class Client:
    """
    Класс для асихронного клиента.
    На входе получает reader и writer
    и реализует методы над ними.
    """
    @logger_decos.log
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.username = 'Guest'

    @logger_decos.log
    def create_presence(self):
        return {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }

    @logger_decos.log
    async def send(self, message):
        self.writer.write(serialize(message))
        await self.writer.drain()

    @logger_decos.log
    async def receive(self):
        data = await self.reader.read(MAX_PACKAGE_LENGTH)
        return deserialize(data)

    @logger_decos.log
    async def close(self):
        # self.send_message(data={ACTION: 'exit'})
        self.writer.close()
        await self.writer.wait_closed()

    @logger_decos.log
    async def send_message(self, data=None):
        if data is None:
            msg = input('Введите сообщение: ')
            # msg = sys.stdin.read()
            if not msg:
                return None
            data = {
                ACTION: SEND,
                TIME: time.time(),
                MESSAGE: msg,
                USER: {
                    ACCOUNT_NAME: self.username
                }
            }
        await self.send(data)
        response = await self.receive()
        if response.get('OK', 400) == 400:
            print('Сообщение не отправлено!')

    @logger_decos.log
    async def send_pressence(self):
        await self.send_message(data=self.create_presence())

    @logger_decos.log
    async def get_messages(self):
        data = {
            ACTION: 'get',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        await self.send(data)
        response = await self.receive()
        if messages := response.get('data'):
            for msg in messages:
                date = datetime.datetime.fromtimestamp(msg.get('date'))
                user = msg.get('user')
                message = msg.get('message')
                print(f'[{date}] {user}: {message}')


async def send_messages(name):
    while True:
        reader, writer = await asyncio.open_connection('localhost', 8888)
        clnt = Client(reader, writer)
        clnt.username = name
        await clnt.send_message()
        await clnt.close()


async def read_messages(name):
    while True:
        reader, writer = await asyncio.open_connection('localhost', 8888)
        clnt = Client(reader, writer)
        clnt.username = name
        await clnt.get_messages()
        await clnt.close()


async def send_pressence(name):
    reader, writer = await asyncio.open_connection('localhost', 8888)
    clnt = Client(reader, writer)
    clnt.username = name
    await clnt.send_pressence()
    await clnt.close()


async def main():
    params = sys.argv
    name = input('Введите имя: ')
    await send_pressence(name)
    if len(params) == 1:
        await asyncio.gather(read_messages(name), send_messages(name), )
    elif params[1] == 'read':
        await read_messages(name)
    elif params[1] == 'send':
        await send_messages(name)


loop = asyncio.new_event_loop()

loop.run_until_complete(main())
