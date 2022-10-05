# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON
# с информацией о заказах. Написать скрипт, автоматизирующий его заполнение
# данными. Для этого:

# Создать функцию write_order_to_json(), в которую передается 5 параметров —
# товар (item), количество (quantity), цена (price), покупатель (buyer),
# дата (date). Функция должна предусматривать запись данных в виде словаря
# в файл orders.json. При записи данных указать величину отступа в 4 пробельных
# символа;
# Проверить работу программы через вызов функции write_order_to_json()
# с передачей в нее значений каждого параметра.

import json

import chardet


def load_from_file(path: str) -> dict | None:
    """
    Считывает из файла словарь, если файл пустой, то возвращает None
    """
    with open(path, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)['encoding']

    with open(path, 'r', encoding=encoding) as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = None

    return data


def write_order_to_json(
        path: str,
        item: str,
        quantity: int,
        price: float,
        buyer: str,
        date: str):
    """
    Добавляет заказ в json файл;
    Файла нет - создает;
    Файл пустой - записывает новые данные;
    В файле нет нужного ключа - создает ключ;
    """

    data = load_from_file(path) or {'orders': []}

    data.setdefault('orders', []).append({'item': item, 'quantity': quantity,
                                          'price': price, 'buyer': buyer, 'date': date})

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


write_order_to_json('orders.json', 'Ручка2', 2, 40,
                    'Иван Иванов', '05/10/2022')
