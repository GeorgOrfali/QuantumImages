import random


class QuantumUtil:

    def generate_random_bit_string(self, length):
        bits = [str(random.randint(0, 1)) for _ in range(length)]
        bit_string = ''.join(bits)
        return bit_string

    def decimal_to_binary(self, decimal, bit_length):
        binary = bin(decimal)[2:]
        padding = bit_length - len(binary)
        binary = '0' * padding + binary
        return binary