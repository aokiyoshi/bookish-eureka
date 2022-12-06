import asyncio
import datetime

import aioconsole
import PySimpleGUI as sg
from common.settings import *
from common.utils import deserialize, now, serialize
from logs import client_log_config, logger_decos
from metaclasses import ClientMeta


class Client(metaclass=ClientMeta):
    @logger_decos.log
    async def send(self, message):
        self.writer.write(serialize(message))
        await self.writer.drain()

    @logger_decos.log
    async def receive(self):
        data = await self.reader.read(MAX_PACKAGE_LENGTH)
        return deserialize(data)

    @logger_decos.log
    def generate_dict(self, action, **kwargs):
        dict = {
            ACTION: action,
            TIME: now(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        return dict | kwargs

    @logger_decos.log
    async def close(self):
        await self.send_data(data=self.generate_dict(action='quit'))
        self.writer.close()
        await self.writer.wait_closed()

    @logger_decos.log
    async def send_data(self, data):
        await self.send(data)
        response = await self.receive()
        if response.get('OK', 400) == 400:
            print('Сообщение не отправлено!')
        else:
            print('>')

    @logger_decos.log
    async def get_data(self, data):
        await self.send(data)
        response = await self.receive()
        if messages := response.get('data', []):
            for msg in messages:
                date = str(msg['date'])
                user = msg.get('user', '')
                message = msg.get('message', '')
                print(f'[{date}] {user}: {message}')

    @logger_decos.log
    async def send_presence(self):
        await self.get_data(self.generate_dict(action=PRESENCE))

    @logger_decos.log
    async def get_new_messages(self):
        await self.get_data(self.generate_dict('get'))
    
    @logger_decos.log
    async def send_message(self, message):
        await self.get_data(self.generate_dict('send', message=message))

    async def init(self, username='Guest'):
        self.reader, self.writer = await asyncio.open_connection(DEFAULT_IP_ADDRESS, DEFAULT_PORT)
        self.username = username

async def test():
    clnt = Client()
    await clnt.init('Hds')
    await clnt.send_presence()
    await clnt.send_message('hey!!!')

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(test())
    except Exception as e:
        print(f'{e=}')