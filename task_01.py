# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий
# выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
# и формирующий новый «отчетный» файл в формате CSV. Для этого:

# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
# с данными, их открытие и считывание данных. В этой функции из считанных данных
# необходимо с помощью регулярных выражений извлечь значения параметров
#
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
#
# Значения каждого параметра поместить в соответствующий список.
# Должно получиться четыре списка — например, os_prod_list, os_name_list,
# os_code_list, os_type_list. В этой же функции создать главный список для
# хранения данных отчета — например, main_data — и поместить в него названия
# столбцов отчета в виде списка: «Изготовитель системы», «Название ОС»,
# «Код продукта», «Тип системы». Значения для этих столбцов также оформить
# в виде списка и поместить в файл main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
# В этой функции реализовать получение данных через вызов функции get_data(),
# а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv().
 

import csv
import re

import chardet


def parse_file(path: str) -> tuple:
    """
    Возвращает кортеж строк, состоящий из значений полей, взятых из файла.
    """

    # Определяем кодировку файла
    with open(path, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)['encoding']

    # Читаем файл
    with open(path, encoding=encoding) as file:
        result = re.findall(
            r'^(?:Изготовитель системы|Название ОС|Код продукта|Тип системы)\s*:\s*(.*)\n',
            file.read(),
            flags=re.MULTILINE
        )

    return (result[2], result[0], result[1], result[3])


def get_data(files: tuple | list) -> list:
    """
    Возвращает список кортежей, каждый из которых содержит параметры, считанные 
    из файла из files.
    """
    result = [parse_file(path) for path in files]

    return result


def write_to_csv(filename: str):
    """
    Записывает данные, взятые из нескольких файлов в одну csv таблицу.
    """
    headers = ('Изготовитель системы', 'Название ОС',
               'Код продукта', 'Тип системы')
    data = get_data(('info_1.txt', 'info_2.txt', 'info_3.txt'))

    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)


write_to_csv('file.csv')
