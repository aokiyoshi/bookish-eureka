import json
import signal
import sys
import time

from .settings import ENCODING, MAX_PACKAGE_LENGTH


def serialize(message):
    return json.dumps(message).encode(ENCODING)


def deserialize(data):
    try:
        return json.loads(data.decode())
    except json.JSONDecodeError:
        return {'ERROR': 400}


# def _type(value):
#     if isinstance(value, int):
#         return 'INTEGER'
#     elif isinstance(value, float):
#         return 'NUMERIC'
#     else:


def now():
    return int(time.time())
