import re


def do_reformatting_address(address: str):
    """Форматирует адресс переставляя слово "улицца" и части названия <улицы>
     Возвращает отформтатированный адрес
     """
    tmp = address.split(' ')
    if len(tmp) == 7.0:
        tmp[4], tmp[5] = tmp[5], tmp[4]
        tmp = ' '.join(tmp)
        return tmp
    elif len(tmp) == 8.0:
        tmp[4], tmp[6] = tmp[6], tmp[4]
        tmp = ' '.join(tmp)
        return tmp
    else:
        print(f'For address {address} len is {len(tmp)} that bigger 7 and 8')
        return False


def address_handler(address: str):
    """Предварительная обработка формата написания адреса"""
    address = address.strip()

    d = {
        'Березовая': 'Берёзовая',
        'Дежнева': 'Дежнёва',
        'Елочная': 'Ёлочная',
        'Ильичева': 'Ильичёва',
        'Минеров': 'Минёров',
        'Могилевская': 'Могилёвская',
        'Муравьева-Амурского': '',
        'Проселочная': 'Просёлочная',
        'Семеновская': 'Семёновская',
        'Тополевая': 'Тополёвая',
        'Черемуховая': 'Черёмуховая',
        'Четвертая': 'Четвёртая',
    }

    for name, replacement in d.items():
        if name in address:
            address = address.replace(name, replacement)
            break

    if 'Проспект.' in address:
        address = address.replace('Проспект.', 'проспект')
    elif 'пр-кт.' in address:
        address = address.replace('пр-кт.', 'проспект')
    elif 'ул.' in address:
        address = address.replace('ул.', 'улица')
    elif 'пер.' in address:
        address = address.replace('пер.', 'переулок')
    elif 'тер.' in address:
        address = address.replace('тер. Бухта', 'улица')

    # del ', д.'
    if 'д.' in address:
        address = address.replace(', д.', '')

    # del ', лит. '
    if ', лит. ' in address:
        address = address.replace(', лит. ', '')

    # del ', к. .'
    if re.search(r',\s[кКkK]\.\s\.', address):
        address = address.replace(', к. .', '')

    # 40, к. а --> 40а
    if re.search(r',\s*[кКkK]\.\s*(?=[А-Яа-яЁё])', address):
        address = address.replace(', к. ', '')
    # 40, к. 1 --> 40
    elif re.search(r',\s*[кКkK]\.\s*1', address):
        address = address.replace(', к. 1', '')
    # 40, к. 2 --> 40/2
    elif re.search(r',\s*[кКkK]\.\s*[^1]', address):
        address = address.replace(', к. ', '/')

    # 40, стр. 2 --> 40/2
    if re.search(r',\s*стр.\s*\d+', address):
        address = address.replace(', стр. ', '/')
    # 40, стр. а --> 40а
    elif re.search(r',\s*стр.\s*.[^\d]', address):
        address = address.replace(', стр. ', '')

    # 26-б --> 26б
    if re.search(r"\s\d+-\w+$", address):
        pattern = r"\s\d+-\w+$"
        match = re.search(pattern, address)
        tmp = match[0].split('-')
        repl = tmp[0] + tmp[1]
        address = re.sub(pattern, repl, address)

    # 120 "А" -- > 120 А
    if re.search(r'"', address):
        address = address.replace('"', '')
    # 120 А -- > 120А
    if re.search(r"\d+\s[А-Яа-яЁё]$", address):
        pattern = r"\d+\s[А-Яа-яЁё]$"
        match = re.search(pattern, address)
        tmp = match[0].split(' ')
        repl = tmp[0] + tmp[1]
        address = re.sub(pattern, repl, address)

    return address


def drop_one_time(df: object):
    """Удаляет строки из датафрейма по которым не возможно произвести геокодирование"""
    # del 'тер. Бухта Горностай, д. №99'
    df.drop(df[(df['address'].str.contains(r'Горностай', regex=True))].index, inplace=True)

    # del '...ул. Зейская, д. 4/2/0'
    df.drop(df[(df['address'].str.contains(r'/\d/\d', regex=True))].index, inplace=True)

    # del '...(дубль X)', '...(инв.№ 166)', '...д. 8/общ, к. (1 этаж)'
    df.drop(df[(df['address'].str.contains(r'(?:\(|\))', regex=True))].index, inplace=True)

    # del 'строительный тип 1'
    df.drop(df[(df['address'].str.contains(r'\sтип\s\d', regex=True))].index, inplace=True)

    # del 'край. Приморский, г. Владивосток, улица Ивановская 4 ДОС 10'
    df.drop(df[(df['address'].str.contains(r'ДОС', regex=True))].index, inplace=True)

    # del ', к. 0, стр. 0'
    index = df[(df['address'].str.contains(r'ул\. Строительная 2-я, д\. 17', regex=True))].index
    df.address[index] = df.address[index].replace(', к. 0, стр. 0', '')

