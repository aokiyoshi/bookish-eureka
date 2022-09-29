# 5. Написать код, который выполняет пинг веб-ресурсов yandex.ru, youtube.com
# и преобразовывает результат из байтовового типа данных в строковый без ошибок
# для любой кодировки операционной системы

import platform
import subprocess
import sys


param = "-n" if platform.system().lower() == "windows" else "-c"
args = ['ping', param, '5', 'ya.ru']
encoding = sys.getdefaultencoding()

subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_ping.stdout:
    print(line.decode(encoding))
