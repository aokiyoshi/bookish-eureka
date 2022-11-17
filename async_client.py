import asyncio
import datetime
import time

from common.settings import *
from common.utils import deserialize, serialize
from logs import client_log_config, logger_decos
import aioconsole
import dis


class ClientMeta(type):
    """
    Метакласс, который проверяет, что у класса Client не должны быть
    использованы методы 'accept', 'listen' и 'socket'
    """
    def __new__(cls, clsname, bases, clsdict):
        for _, value in clsdict.items():
            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.argval in ('accept', 'listen', 'socket'):
                        raise ValueError(
                            'Класс не должен содержать вызовов accept!')

        return type.__new__(cls, clsname, bases, clsdict)


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
    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    @logger_decos.log
    def generate_dict(self, action, message=None):
        dict = {
            ACTION: action,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        if message is not None:
            dict.setdefault(MESSAGE, message)
        return dict

    @logger_decos.log
    async def send_data(self, data):
        await self.send(data)
        response = await self.receive()
        if response.get('OK', 400) == 400:
            await aioconsole.aprint('Сообщение не отправлено!')

    @logger_decos.log
    async def send_presence(self):
        await self.send_data(self.generate_dict(action=PRESENCE))

    @logger_decos.log
    async def send_message(self):
        msg = await aioconsole.ainput('>>> ')
        if not msg:
            return False
        if msg == '!exit':
            await self.close()
        await self.send_data(self.generate_dict(action=SEND, message=msg))

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
                await aioconsole.aprint(f'[{date}] {user}: {message}')

    async def init(self):
        self.reader, self.writer = await asyncio.open_connection('localhost', 8888)
        name = input('Введите имя: ')
        self.username = name
        await self.send_presence()

        while True:
            try:
                await self.get_messages()
                await self.send_message()
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
            loop.close()


if __name__ == "__main__":

    clnt = Client()
    clnt.start()
