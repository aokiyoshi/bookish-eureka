import json
import signal
import sys
import time

from models import Token

from .settings import ENCODING, MAX_PACKAGE_LENGTH


def serialize(message):
    return json.dumps(message).encode(ENCODING)


def deserialize(data):
    try:
        return json.loads(data.decode())
    except json.JSONDecodeError:
        return {'ERROR': 400}

def now():
    return int(time.time())


def login_required(func):
    def wrapper(*args, **kwargs):
        username = args[1].get('user', {}).get('account_name', '')
        token = args[1].get('user', {}).get('token', '')

        if not Token.check_given_token(token, username):
            return {'OK': 200, 'messages': ['Нужно залогиниться']}

        return func(*args, **kwargs)
    return wrapper
