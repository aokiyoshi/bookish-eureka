import inspect
import logging
import sys
import traceback


import logs.client_log_config
import logs.server_log_config


def log(func_to_log):
    def log_saver(*args, **kwargs):
        logger_name = 'server' if 'async_serv.py' in sys.argv[0] else 'client'
        LOGGER = logging.getLogger(logger_name)

        result = func_to_log(*args, **kwargs)
        LOGGER.debug(f'Функция {func_to_log.__name__} вызывается из функции '
                    f'{traceback.format_stack()[0].strip().split()[-1]} '
                    f'с аргументами {args}, {kwargs}. '
                    f'Вызваший модуль: {func_to_log.__module__}'
                    )

        return result
    return log_saver
