# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор».
# Далее забыть о том, что мы сами только что создали этот файл и исходить из того,
# что перед нами файл в неизвестной кодировке.
# Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того,
# в какой кодировке он был создан.


import chardet

# Устанавливаем начальные параметры
file_name = 'my_file.txt'
words_list = ['сетевое программирование', 'сокет', 'декоратор']

# Записываем строки в файл
with open(file_name, 'w') as file:
    file.writelines('\n'.join(words_list))

# Определяем кодировку вышесозданного файла
with open(file_name, 'rb') as file:
    rawdata = file.read()
    encoding = chardet.detect(rawdata)['encoding']
    print(f'{encoding=}')

# Открываем файл с кодировкой, которую определели выше
with open(file_name, 'r', encoding=encoding) as file:
    print(''.join(file.readlines()))
