from common.settings import DEFAULT_PORT


class NonNegative:
    """Дескриптор на положительное значение порта"""

    def __init__(self, port):
        self.port = port

    def __get__(self, instance, owner):
        return instance.__dict__[self.port]

    def __set__(self, instance, value):
        if value < 0:
            print(
                f'Номер порта не должен быть отрицательным числом.',
                f'Выставлен порт {DEFAULT_PORT}'
            )
            instance.__dict__[self.port] = DEFAULT_PORT
        else:
            instance.__dict__[self.port] = value

    def __delete__(self, instance):
        del instance.__dict__[self.port]
