# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard»
# из строкового представления в байтовое и выполнить обратное преобразование
# (используя методы encode и decode)


def convert_to_bytes(string: str) -> bytes:
    return string.encode('utf-8')


word_list = ('разработка', 'администрирование', 'protocol', 'standard')

for word in word_list:
    print(
        f'{word}: {convert_to_bytes(word)} {type(convert_to_bytes(word))}')
