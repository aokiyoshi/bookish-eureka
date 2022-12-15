import dis


class ServerMeta(type):
    """
    Метакласс, который проверяет, что у класса Server не должны быть
    использованы методы 'connect'
    """
    def __new__(cls, clsname, bases, clsdict):
        for _, value in clsdict.items():
            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.argval in ('connect', 'tcp'):
                        raise ValueError(
                            'Класс не должен содержать вызовов connect!')

        return type.__new__(cls, clsname, bases, clsdict)


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
