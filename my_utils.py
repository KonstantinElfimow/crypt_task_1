import numpy as np


def add_bin_data_to_file(path_to: str, data: list) -> bool:
    try:
        with open(path_to, 'rb+') as f:
            f.seek(0, 2)  # перемещение курсора в конец файла
            for d in data:
                f.write(d)  # собственно, запись
            return True
    except FileNotFoundError:
        print("Невозможно открыть файл")
        return False


def entropy(labels: bytearray) -> float:
    """ Вычисление энтропии вектора из 0-1 """
    n_labels = len(labels)

    if n_labels <= 1:
        return 0

    counts = np.bincount(labels)
    probs = counts[np.nonzero(counts)] / n_labels
    n_classes = len(probs)

    if n_classes <= 1:
        return 0
    return - np.sum(probs * np.log(probs)) / np.log(n_classes)


def cyclic_shift(value, width: int, shift: int):
    """ Побитовый циклический сдвиг числа.
        value < 0 - циклический сдвиг вправо.
        value > 0 - циклический сдвиг влево"""
    if shift == 0:
        return value
    # Преобразование числа в его битовое представление
    temp = '{:0{width}b}'.format(value, width=width)[::1]
    # Циклический сдвиг (с помощью слайсов) и преобразование из строки в тип value
    temp = type(value)(int(temp[shift:] + temp[:shift], base=2))
    return temp


def cast_np_uint(value, width_old: int, ntype: type, width_new: int):
    """ Функция создана с целью преобразования из длинных
        беззнаковых целых чисел в более короткие беззнаковые
        целые числа. Длина ntype должна совпадать c width_new. """
    # Преобразование числа в его бинарное представление, начиная с младшего разряда
    binary = '{:0{width}b}'.format(value, width=width_old)[::-1]
    i = 0
    res = 0
    while i < len(binary) and i < width_new:
        res += int(binary[i]) * (2 ** i)
        i += 1
    res = ntype(res)
    return res


def to_bits(value, width: int) -> str:
    """ Преобразование числа в его битовое представление """
    return '{:0{width}b}'.format(value, width=width)[::1]
