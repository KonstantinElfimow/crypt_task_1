import numpy as np
from my_utils import cyclic_shift, cast_np_uint, to_bits
import my_Feistel_network
import my_utils


def test():
    # Проверка секретного ключа
    print(my_utils.entropy(bytearray(to_bits(my_Feistel_network._SKEY, 64), "UTF-8")))
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
        my_Feistel_network.crypt_ecb(f'crypt/input/input_{x}.txt', f'crypt/cipher/ecb/cypher_{x}.txt')
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/output/ecb/output_{x}.txt', 'w')
        f.close()
        # Дешифрование в режиме ECB
        my_Feistel_network.decrypt_ecb(f'crypt/cipher/ecb/cypher_{x}.txt', f'crypt/output/ecb/output_{x}.txt')


def task_cbc():
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/cipher/cbc/cypher_{x}.txt', 'w')
        f.close()
        # Шифрование в режиме CBC
        my_Feistel_network.crypt_cbc(f'crypt/input/input_{x}.txt', f'crypt/cipher/cbc/cypher_{x}.txt')
    for x in (1, 2, 3):
        # Чистка файла перед записью
        f = open(f'crypt/output/cbc/output_{x}.txt', 'w')
        f.close()
        # Дешифрование в режиме CBC
        my_Feistel_network.decrypt_cbc(f'crypt/cipher/cbc/cypher_{x}.txt', f'crypt/output/cbc/output_{x}.txt')


if __name__ == '__main__':
    # test()
    task_ecb()
    task_cbc()
