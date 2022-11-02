import asyncio
from dataclasses import dataclass

from common.settings import ACTION, MAX_PACKAGE_LENGTH, TIME
from common.utils import deserialize, serialize
from logs import logger_decos, server_log_config

messages = []
users = {}


@logger_decos.log
def process_message(bdata: bytes):

    # Проверяем, что bdata (binary data) не пустой
    if not bdata:
        return {'ERROR': 406}

    # Десериализуем
    data = deserialize(bdata)

    # Если нет ключа с action в словаре
    if ACTION not in data:
        return {'ERROR': 405}

    # Обрабатываем
    match data[ACTION]:

        # Сообщение присуствия, возвращаем сообщение ОК
        # Пишем сообщение о новом пользователе
        case 'presence':
            user = data.get('user').get('account_name')
            users.setdefault(user, 0)
            messages.append(
                {
                    'user': 'Server',
                    'message': f'{user} присоеденился в чат',
                    'date': data.get(TIME),
                }
            )
            return {'OK': 200}

        # Получить новые сообщения, если новых сообщений нет, возвращаем пустой
        # список. Проверяется словарь users, в котором для конкретного
        # пользователя записано последнее прочитанное сообщение.
        case 'get':
            user = data.get('user').get('account_name')
            num = users.get(user)

            if num == len(messages) - 1:
                return {'OK': 200, 'data': []}

            response = messages[num + 1:]
            users[user] = len(messages) - 1
            return {'OK': 200, 'data': response}

        # Отправить сообщение, если все нормально записываем сообщение в список и
        # клиенту возвращаем код 200
        case 'send':
            messages.append(
                {
                    'user': data.get('user').get('account_name'),
                    'message': data.get('message'),
                    'date': data.get(TIME),
                }
            )
            return {'OK': 201}

        # Заглушка на будущее. Если с сервером будет непрерывная взять и
        # будет необходимость ее закрывать.
        case 'exit':
            return {}

        # Возвращаем ошибку, если действие какое-то другое
        case _:
            return {'ERROR': 'Неизвестное действие'}


@logger_decos.log
async def handle_conn(reader, writer):
    data = await reader.read(MAX_PACKAGE_LENGTH)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    response = process_message(data)

    writer.write(serialize(response))
    await writer.drain()
    print("Close the connection")
    writer.close()


@logger_decos.log
async def main():
    server = await asyncio.start_server(
        handle_conn, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Сервер запущен на {addrs}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Сервер отключен. До свидания!')