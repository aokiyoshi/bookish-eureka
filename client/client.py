import asyncio

from common.settings import (ACCOUNT_NAME, ACTION, DEFAULT_IP_ADDRESS,
                             DEFAULT_PORT, MAX_PACKAGE_LENGTH, PRESENCE, TIME,
                             USER, QUIT)
from common.utils import deserialize, now, serialize
from logs import logger_decos
from common.metaclasses import ClientMeta


class Client(metaclass=ClientMeta):

    @logger_decos.log
    async def send(self, message):
        """
        Метод для отправки сообщения на сервер
        """
        self.writer.write(serialize(message))
        await self.writer.drain()

    @logger_decos.log
    async def receive(self):
        """
        Метод для приема сообщения из сервера
        """
        data = await self.reader.read(MAX_PACKAGE_LENGTH)
        return deserialize(data)

    @logger_decos.log
    def generate_dict(self, action, **kwargs):
        """
        Генерирует словарь для протокола JIM
        """
        dict = {
            ACTION: action,
            TIME: now(),
            USER: {
                ACCOUNT_NAME: self.username,
                'token': self.token
            }
        }
        return dict | kwargs

    @logger_decos.log
    async def close(self):
        await self.send_data(
            data=self.generate_dict(action=QUIT)
        )
        self.writer.close()
        await self.writer.wait_closed()

    @logger_decos.log
    async def get_data(self, data):
        await self.send(data)
        response = await self.receive()
        messages = response.get('messages', [])
        if messages:
            for msg in messages:
                print(msg)

        return response

    @logger_decos.log
    async def init(self, username='Guest'):
        self.reader, self.writer = await asyncio.open_connection(
            DEFAULT_IP_ADDRESS, DEFAULT_PORT
        )
        self.username = username
        self.token = ''

    @logger_decos.log
    async def send_presence(self):
        await self.get_data(self.generate_dict(action=PRESENCE))

    @logger_decos.log
    async def get_new_messages(self, sender=None):
        await self.get_data(self.generate_dict('get', sender=sender))

    @logger_decos.log
    async def send_message(self, message, reciever=None):

        if message.startswith('!add'):
            for contact in message.split(' ')[1:]:
                await self.get_data(
                    self.generate_dict('add_contact', contact=contact)
                )
            return

        if message.startswith('!login'):
            _, username, password = message.split(' ')
            response = await self.get_data(
                self.generate_dict(
                    'login', username=username, password=password)
            )
            self.token = response.get('data', '')
            if self.token:
                self.username = username
                return True

            return False

        await self.get_data(
            self.generate_dict('send', message=message, reciever=reciever)
        )

    @logger_decos.log
    async def get_contact_list(self):
        await self.send(self.generate_dict('get_contacts'))
        data = await self.receive()
        return [contact['user'] for contact in data.get('data', [])]


async def test():
    clnt = Client()
    await clnt.init()
    await clnt.send_message('!login Test www')
    await clnt.send_message('hey!!!')
    print(await clnt.get_contact_list())

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(test())
    except KeyboardInterrupt as e:
        print(f'{e=}')
