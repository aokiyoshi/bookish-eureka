import asyncio
import datetime
import time

import aioconsole

from common.settings import *
from common.utils import deserialize, now, serialize
from logs import client_log_config, logger_decos
from metaclasses import ClientMeta


class Client(metaclass=ClientMeta):
    username = 'Guest'

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
        print(f"{data=} ||| {response=}")
        if response.get('OK', 400) == 400:
            print('Сообщение не отправлено!')

    @logger_decos.log
    async def send_presence(self):
        await self.send_data(self.generate_dict(action=PRESENCE))

    @logger_decos.log
    async def get_data(self, data):
        await self.send(data)
        response = await self.receive()
        if messages := response.get('data', []):
            for msg in messages:
                date = datetime.datetime.fromtimestamp(float(msg['date']))
                user = msg.get('user', '')
                message = msg.get('message', '')
                print(f'[{date}] {user}: {message}')

    @logger_decos.log
    async def loop(self):
        msg = await aioconsole.ainput('>>> ')
        if msg == '':
            await self.get_data(self.generate_dict('get'))
        elif msg == '!exit':
            await self.close()
        elif msg == '!contacts':
            await self.get_data(self.generate_dict(action='get_contacts'))
        elif msg.split(' ')[0] == '!add' and msg.split(' ')[1]:
            await self.send_data(self.generate_dict(action='add_contact', contact=msg.split(' ')[1]))
        else:
            await self.send_data(self.generate_dict(action=SEND, message=msg))

    async def init(self):
        self.reader, self.writer = await asyncio.open_connection(DEFAULT_IP_ADDRESS, DEFAULT_PORT)
        name = input('Введите имя: ')
        self.username = name
        await self.send_presence()

        while True:
            try:
                await self.loop()
            except asyncio.exceptions.TimeoutError:
                pass

    def start(self):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.init())
        except KeyboardInterrupt:
            print('Работа программы завершена.')
        except ConnectionResetError:
            print('Работа программы завершена при помощи команды exit')
        finally:
            asyncio.run(self.close())
            loop.close()


if __name__ == "__main__":

    clnt = Client()
    clnt.start()
