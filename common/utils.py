import json
import signal
import sys

from .settings import ENCODING, MAX_PACKAGE_LENGTH


def get_message(socket):
    response = socket.recv(MAX_PACKAGE_LENGTH)
    return json.loads(response.decode(ENCODING))
    
def send_message(socket, msg):
    if not isinstance(msg, dict):
        return 'Ошибка при отправки сообщения {msg}. Не явялется словарем.'

    js_message = json.dumps(msg)
    encoded_message = js_message.encode(ENCODING)

    socket.send(encoded_message)

    return 'ОК. Сообщение {msg} Отправлено'

def init_sygnal():
    signal.signal(signal.SIGINT, signal_handler)

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)
