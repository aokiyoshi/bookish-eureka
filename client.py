import asyncio

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
    async def get_data(self, data):
        await self.send(data)
        response = await self.receive()
        messages = response.get('data', [])
        if messages:
            for msg in messages:
                date = msg.get('date', '')
                user = msg.get('user', '')
                message = msg.get('message', '')
                print(f'[{date}] {user}: {message}')
                
    @logger_decos.log
    async def init(self, username='Guest'):
        self.reader, self.writer = await asyncio.open_connection(DEFAULT_IP_ADDRESS, DEFAULT_PORT)
        self.username = username

    @logger_decos.log
    async def send_presence(self):
        await self.get_data(self.generate_dict(action=PRESENCE))

    @logger_decos.log
    async def get_new_messages(self, sender=None):
        await self.get_data(self.generate_dict('get', sender=sender))

    @logger_decos.log
    async def send_message(self, message, reciever=None):
        if message.startswith('!contacts'):
            return await self.get_data(self.generate_dict('get_contacts'))

        if message.startswith('!add'):
            for contact in message.split(' ')[1:]:
                await self.get_data(self.generate_dict('add_contact', contact=contact))
            return

        await self.get_data(self.generate_dict('send', message=message, reciever=reciever))

    @logger_decos.log
    async def get_contact_list(self):
        await self.send(self.generate_dict('get_contacts'))
        data = await self.receive()
        return [contact['user'] for contact in data.get('data', [])]


async def test():
    clnt = Client()
    await clnt.init('Yoshi')
    await clnt.send_presence()
    await clnt.send_message('hey!!!')
    print(await clnt.get_contact_list())

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(test())
    except Exception as e:
        print(f'{e=}')
