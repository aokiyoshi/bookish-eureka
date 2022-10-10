from numpy import isin
from .settings import MAX_PACKAGE_LENGTH, ENCODING
import json

class CommonMixin:

    def get_message(self):
        response = self.client.recv(MAX_PACKAGE_LENGTH)
        return json.loads(response.decode(ENCODING))
        
    def send_message(self, msg):
        if not isinstance(msg, dict):
            raise TypeError

        js_message = json.dumps(msg)
        encoded_message = js_message.encode(ENCODING)

        self.client.send(encoded_message)
