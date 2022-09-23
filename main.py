import numpy as np
from utils import cyclic_shift, cast_np_uint, to_bits
import random


SKEY: np.uint64 = np.uint64(6009866147282825843)  # секретный ключ

ROUNDS: int = 10  # количество проходов по сети Фейстеля

ROUND_KEYS: list = list()  # Создаём раундовые ключи
for index in range(ROUNDS):
    ROUND_KEYS.append(cast_np_uint((cyclic_shift(SKEY, 64, -(index + 1)) ^ SKEY), 64, np.uint16, 16))

IV: list = list()  # Вектор инициализации для режима шифрования CBC (увы, не получилось сделать одним числом)
for _ in range(4):
    IV.append(np.uint16(random.randint(0, 65535)))


# Не получилось :(. Хотел читать блок в 8 байт, а только потом разбивать,
# но увы - есть проблемы с приведением типов

# def block_of_64bytes_divided_by_4(B: np.uint64, width: int = 64) -> list:
#     b: list = list()
#     for count in (1, 2, 3, 4):
#         t = tuple([(count - 1) * 16, count * 16 - 1])
#         b.append(np.uint16(take_bits(B, width, t)))
#     return b


def _add_bin_data_to_file(path_to: str, data: list) -> bool:
    try:
        with open(path_to, 'rb+') as f:
            f.seek(0, 2)  # перемещение курсора в конец файла
            for d in data:
                f.write(d)  # собственно, запись
            return True
    except FileNotFoundError:
        print("Невозможно открыть файл")
        return False


def _entropy(labels: bytearray) -> float:
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


def _f1(m0: np.uint16, m1: np.uint16) -> np.uint16:
    """ (m0 <<< 4) + (m1 >> 2) """
    return (cyclic_shift(m0, 16, 4)) + (cyclic_shift(m1, 16, -2))


def _f2(m2: np.uint16, m3: np.uint16.numerator) -> np.uint16:
    """ (m2 <<< 7) ^ ~m3 """
    return cyclic_shift(m2, 16, 7) ^ (~m3)


def Ek(message: list) -> list:
    #  ...выполняем преобразование по раундам в соответствии с заданием
    cipher: list = np.copy(message)
    for i in range(ROUNDS):
        cipher[0] = message[2] ^ (~ROUND_KEYS[i])
        cipher[1] = _f1(message[0] ^ ROUND_KEYS[i], message[1]) ^ message[3]
        cipher[2] = _f2(cipher[0], cipher[1]) ^ message[1]
        cipher[3] = message[0] ^ ROUND_KEYS[i]
        message = np.copy(cipher)
    return cipher


def Dk(cipher: list) -> list:
    #  ...выполняем обратное преобразование по раундам в соответствии
    #  с заданием, но не трогаем f (f^-1 - недопустимо)
    message: list = np.copy(cipher)
    for r_i in range(ROUNDS - 1, -1, -1):
        message[0] = cipher[3] ^ ROUND_KEYS[r_i]
        message[1] = _f2(cipher[0], cipher[1]) ^ cipher[2]
        message[2] = cipher[0] ^ (~ROUND_KEYS[r_i])
        message[3] = _f1(cipher[3], message[1]) ^ cipher[1]
        cipher = np.copy(message)
    return message


def crypt_ecb(path_from: str, path_to: str) -> bool:
    try:
        # Открываем файл, сообщение которого нужно зашифровать
        with open(path_from, 'rb') as rfile:
            while True:
                # Проверка конца файла
                file_eof: bytes = rfile.read(1)
                rfile.seek(rfile.tell() - 1)
                if file_eof == b'':
                    break

                # Блок состоит из 4 частей
                message: list = list()
                for _ in range(4):
                    message.append(np.uint16(int.from_bytes(rfile.read(2), byteorder="little", signed=False)))

                #  Шифрование
                cipher: list = Ek(message)
                #  записываем результат в файл
                _add_bin_data_to_file(path_to, cipher)
            return True
    except FileNotFoundError:
        print("Невозможно открыть файл")
        return False


def decrypt_ecb(path_from: str, path_to: str) -> bool:
    try:
        # Открываем файл, сообщение которого нужно расшифровать, и файл, куда записываем расшифрованное сообщение
        with open(path_from, 'rb') as rfile:
            while True:
                # Проверка конца файла
                file_eof: bytes = rfile.read(1)
                rfile.seek(rfile.tell() - 1)
                if file_eof == b'':
                    break

                # Блок состоит из 4 частей
                cipher: list = list()
                for _ in range(4):
                    cipher.append(np.uint16(int.from_bytes(rfile.read(2), byteorder="little", signed=False)))

                #  Дешифрование
                message: list = Dk(cipher)
                #  записываем результат в файл
                _add_bin_data_to_file(path_to, message)
            return True
    except FileNotFoundError:
        print("Невозможно открыть файл")
        return False


def xor_for_cbc(message: list, cipher: list) -> list:
    temp: list = list()
    for i in range(4):
        temp.append(np.uint16(message[i] ^ cipher[i]))
    return temp


def crypt_cbc(path_from: str, path_to: str) -> bool:
    try:
        # Открываем файл, сообщение которого нужно зашифровать
        with open(path_from, 'rb') as rfile:
            # блок зашифрованного текста и синхропосылка одновременно
            cipher: list = np.copy(IV)
            while True:
                # Проверка конца файла
                file_eof: bytes = rfile.read(1)
                rfile.seek(rfile.tell() - 1)
                if file_eof == b'':
                    break

                # Блок состоит из 4 частей
                message: list = list()
                for _ in range(4):
                    message.append(np.uint16(int.from_bytes(rfile.read(2), byteorder="little", signed=False)))

                #  Шифрование
                cipher = Ek(xor_for_cbc(message, cipher))
                #  записываем результат в файл
                _add_bin_data_to_file(path_to, cipher)
            return True
    except FileNotFoundError:
        print("Невозможно открыть файл")
        return False


def decrypt_cbc(path_from: str, path_to: str) -> bool:
    try:
        # Открываем файл, сообщение которого нужно расшифровать, и файл, куда записываем расшифрованное сообщение
        with open(path_from, 'rb') as rfile:
            # блок открытого текста и синхропосылка одновременно
            message: list = np.copy(IV)
            while True:
                # Проверка конца файла
                file_eof: bytes = rfile.read(1)
                rfile.seek(rfile.tell() - 1)
                if file_eof == b'':
                    break

                # Блок состоит из 4 частей
                cipher: list = list()
                for _ in range(4):
                    cipher.append(np.uint16(int.from_bytes(rfile.read(2), byteorder="little", signed=False)))

                #  Дешифрование
                message = xor_for_cbc(message, Dk(cipher))
                #  записываем результат в файл
                _add_bin_data_to_file(path_to, message)
            return True
    except FileNotFoundError:
        print("Невозможно открыть файл")
        return False


def test():
    # Проверка секретного ключа
    print(_entropy(bytearray(to_bits(SKEY, 64), "UTF-8")))
    print('\n')
    # Проверка реализации циклического побитового сдвига для беззнаковых чисел
    a = np.uint16(5743)
    print(to_bits(a, 16))
    a = cyclic_shift(a, 16, -2)
    print(to_bits(a, 16))
    print('\n')
    # Проверка реализации uint_cast. В данном примере из 64 бит приводятся только биты с индексом 0...15
    b = np.uint64(2131221312122121)
    print(to_bits(b, 64))
    b = cast_np_uint(b, 64, np.uint16, 16)
    print(to_bits(b, 16))


def task_ecb():
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/cipher/ecb/cypher_{x}.txt', 'w')
        f.close()
        # Шифрование в режиме ECB
        crypt_ecb(f'crypt/input/input_{x}.txt', f'crypt/cipher/ecb/cypher_{x}.txt')
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/output/ecb/output_{x}.txt', 'w')
        f.close()
        # Дешифрование в режиме ECB
        decrypt_ecb(f'crypt/cipher/ecb/cypher_{x}.txt', f'crypt/output/ecb/output_{x}.txt')


def task_cbc():
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/cipher/cbc/cypher_{x}.txt', 'w')
        f.close()
        # Шифрование в режиме CBC
        crypt_ecb(f'crypt/input/input_{x}.txt', f'crypt/cipher/cbc/cypher_{x}.txt')
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/output/cbc/output_{x}.txt', 'w')
        f.close()
        # Дешифрование в режиме CBC
        decrypt_ecb(f'crypt/cipher/cbc/cypher_{x}.txt', f'crypt/output/cbc/output_{x}.txt')


if __name__ == '__main__':
    # test()
    task_ecb()
    task_cbc()
