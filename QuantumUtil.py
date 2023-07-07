import random
import itertools


class QuantumUtil:

    def generate_binary_combinations(self, n):
        binary_dict = {}
        for i in range(2 ** n):
            binary = bin(i)[2:].zfill(n)
            binary_dict[binary] = 0

        return binary_dict

    def generate_random_bit_string(self, length):
        bits = [str(random.randint(0, 1)) for _ in range(length)]
        bit_string = ''.join(bits)
        return bit_string

    def decimal_to_binary(self, decimal, bit_length):
        binary = bin(decimal)[2:]
        padding = bit_length - len(binary)
        binary = '0' * padding + binary
        return binary

    def remove_zero_values(self, dictionary):
        return {key: value for key, value in dictionary.items() if value != 0}

    def enumerate(self, iterable, begin=0, limit=None):
        iterator = itertools.islice(iterable, begin, begin + limit) if limit is not None else iterable
        for index, item in enumerate(iterator, begin):
            yield index, item