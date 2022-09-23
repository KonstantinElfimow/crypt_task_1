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


def take_bits(value, width: int, from_i1_to_i2: tuple) -> int:
    """ Функция создана с целью преобразования из длинных
        беззнаковых целых чисел в более короткие беззнаковые
        целые числа. Длина ntype должна совпадать c width_new. """
    # Преобразование числа в его бинарное представление, начиная с младшего разряда
    binary = '{:0{width}b}'.format(value, width=width)[::-1]

    res = 0
    for i in range(from_i1_to_i2[0], from_i1_to_i2[1] + 1):
        res += int(binary[i]) * (2 ** i)
    return res


def to_bits(value, width: int) -> str:
    # Преобразование числа в его битовое представление
    return '{:0{width}b}'.format(value, width=width)[::1]


# def right_shift_uint(value, width: int, shift: int):
#     if shift >= width:
#         return type(value)(int(to_bits(0, width), base=2))
#
#     binary = to_bits(value, width)
#     res = 0
#     for i in range(shift, width):
#         res += int(binary[i]) * (2 ** i)
#         i += 1
#     res = type(value)(res)
#     return res
