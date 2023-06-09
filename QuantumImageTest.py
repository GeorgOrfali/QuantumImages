from QuantumImage import *
from QuantumUtil import *
from QuantumImageEncryption import *


class QuantumImageTest:
    image = []
    qImageArray = []
    qKeyImageArray = []
    qImage = None
    qKeyImage = None
    width = 0
    height = 0
    color = 0
    util = QuantumUtil()

    def TestCasesWithTerminalOutput(self, posX, posY, color):
        print("Starting the Test!")
        qImage = QuantumImage()
        qImage.setCircuitWithArray(self.image, self.color)
        print("---------------------------------------------------")
        position = posX + posY
        if len(position) >= len(color):
            print('Input: ', position + color)
        else:
            print('Input: ', color + position)
        qImage.circuit.getStates()
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
        qImage.circuit.getStates()
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
        self.qImage = QuantumImage()
        self.qImage.setCircuitWithArray(self.image, self.color)
        position = self.qImage.circuit.xqubits + self.qImage.circuit.yqubits
        self.qImage.circuit.getStates()
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                self.qImage.encodeColor(self.util.decimal_to_binary(xi, self.qImage.circuit.xqubits),
                                        self.util.decimal_to_binary(yi, self.qImage.circuit.yqubits),
                                        color)

        self.qImage.circuit.getStates()
        self.qImageArray = sorted(self.qImage.circuit.states, key=lambda x: x[:position])
        # After encoding, create key Image and encrypt the Quantum Image
        self.qKeyImage = QuantumKeyImage(self.qImage.circuit.width, self.qImage.circuit.height, self.color)
        self.qKeyImage.qImage.circuit.getStates()
        self.qKeyImageArray = sorted(self.qKeyImage.qImage.circuit.states, key=lambda x: x[:position])

    def generate_random_image(self, width, height, color):
        self.image = []
        self.width = width
        self.height = height
        self.color = color

        for h in range(height):
            row = []
            for w in range(width):
                row.append(self.util.generate_random_bit_string(color))
            self.image.append(row)

    def getImage(self):
        result = ""
        for row in self.image:
            result = result + "["
            for e in row:
                result = result + " " + str(e)
            result = result + " ]\n"
        return result

    def getQuantumImage(self, qImage, qImageArray):
        result = ""
        open = False
        if qImage is not None:
            position = qImage.circuit.xqubits + qImage.circuit.yqubits
        for i, color in enumerate(qImageArray):
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
            result = result + " " + str(color[position:]) + " "
            if i == len(qImageArray) - 1:
                result = result + "]"
        return result
