# 3. Определить, какие из слов «attribute», «класс», «функция», «type»
# невозможно записать в байтовом типе. Важно: решение должно быть универсальным,
# т.е. не зависеть от того, какие конкретно слова мы исследуем.


def can_be_converted_to_bytes(string: str) -> bool:
    """
    Возвращает True если переданный аргумент можно
    преобразовать в битовый тип. 
    В противном случае  возвращает False.
    """
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


word_list = ('attribute', 'класс', 'функция', 'type')

for word in word_list:
    print(
        f'Слово "{word}" {"можно" if can_be_converted_to_bytes(word) else "нельзя"} записать в байтовом типе.')
