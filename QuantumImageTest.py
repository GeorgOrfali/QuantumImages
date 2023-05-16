import math
import random
from QuantumImage import *


class QuantumImageTest:
    image = []
    qImageArray = []
    qImage = None
    width = 0
    height = 0
    color = 0

    def TestCasesWithTerminalOutput(self, posX, posY, color):
        print("Starting the Test!")
        qImage = QuantumImage(self.image, self.color)
        print("---------------------------------------------------")
        position = posX + posY
        if len(position) >= len(color):
            print('Input: ', position + color)
        else:
            print('Input: ', color + position)
        qImage.getStates()
        before = ''
        after = ''

        if len(position) >= len(color):
            before = qImage.getCurrentClusterBits(position)
        else:
            before = qImage.getCurrentClusterBits(color)
        print("Before: ", before)
        if before is None:
            print('\033[91m Failed!', '\033[0m')
            print("---------------------------------------------------")
        qImage.encodeColor(posX, posY, color)
        qImage.getStates()
        if len(position) >= len(color):
            after = qImage.getCurrentClusterBits(position)
        else:
            after = qImage.getCurrentClusterBits(color)
        print("After: ", after)
        if len(position) >= len(color):
            if after == position + color:
                print('\033[92m Success!', '\033[0m')
                print("---------------------------------------------------")
            else:
                print('\033[91m Failed!', '\033[0m')
                print("---------------------------------------------------")
        else:
            if after == color + position:
                print('\033[92m Success!', '\033[0m')
                print("---------------------------------------------------")
            else:
                print('\033[91m Failed!', '\033[0m')
                print("---------------------------------------------------")

    def TestCasesWithArrayOutput(self):
        print("Starting the Simulation!")
        self.qImage = QuantumImage(self.image, self.color)
        position = self.qImage.xqubits + self.qImage.yqubits
        self.qImage.getStates()
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                self.qImage.encodeColor(self.decimal_to_binary(xi, self.qImage.xqubits),
                                        self.decimal_to_binary(yi, self.qImage.yqubits),
                                        color)
        #After enconding set all redundant colors or position to an dump state
        self.encodeRedundancies()
        self.qImage.getStates()
        if len(self.qImage.posQubits) >= len(self.qImage.colorQubits):
            self.qImageArray = sorted(self.qImage.states, key=lambda x: x[:position])
        else:
            self.qImageArray = sorted(self.qImage.states, key=lambda x: x[len(self.qImage.colorQubits):])

    def encodeRedundancies(self):
        countPixels = sum(len(sublist) for sublist in self.image)
        if len(self.qImage.states) > countPixels:
            if self.qImage.cqubits > len(self.qImage.posQubits):
                print("Encode Redundancies!")
                #Copy array
                states = list(self.qImage.states)
                #change all unused to redudant information for position 1111 for color 0000
                for column in self.image:
                    for color in column:
                        found = False
                for state in states:
                    found = False
                    for column in self.image:
                        for color in column:
                            if color == state[:self.qImage.cqubits]:
                                found = True
                    if not found:
                        #Get max value for x and max value for y in decimal
                        x = 2 ** self.qImage.xqubits - 1
                        y = 2 ** self.qImage.yqubits - 1
                        self.qImage.encodeColor(self.decimal_to_binary(x, self.qImage.xqubits),
                                                self.decimal_to_binary(y, self.qImage.yqubits),
                                                state[:self.qImage.cqubits])
    def generate_random_image(self, width, height, color):
        self.image = []
        self.width = width
        self.height = height
        self.color = color

        for h in range(height):
            row = []
            for w in range(width):
                row.append(self.generate_random_bit_string(color))
            self.image.append(row)

    def getImage(self):
        result = ""
        for row in self.image:
            result = result + "["
            for e in row:
                result = result + " " + str(e)
            result = result + " ]\n"
        return result

    def getQuantumImage(self):
        result = ""
        open = False
        if self.qImage is not None:
            position = self.qImage.xqubits + self.qImage.yqubits
        for i, color in enumerate(self.qImageArray):
            if i % position == 0:
                if not open:
                    if i == 0:
                        result = result + "["
                        open = True
                    else:
                        result = result + "]\n["
                        open = True
                elif open:
                    result = result + "]\n["
                    open = False
            result = result + " " + str(color) + " "
            if i == len(self.qImageArray) - 1:
                result = result + "]"
        return result

    def generate_random_bit_string(self, length):
        bits = [str(random.randint(0, 1)) for _ in range(length)]
        bit_string = ''.join(bits)
        return bit_string

    def decimal_to_binary(self, decimal, bit_length):
        binary = bin(decimal)[2:]
        padding = bit_length - len(binary)
        binary = '0' * padding + binary
        return binary
