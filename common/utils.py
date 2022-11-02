import json
import signal
import sys

from .settings import ENCODING, MAX_PACKAGE_LENGTH


def serialize(message):
    return json.dumps(message).encode(ENCODING)

def deserialize(data):
    try:
        return json.loads(data.decode())
    except json.JSONDecodeError:
        return {'ERROR': 400}

