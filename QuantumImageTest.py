from QuantumCircuit import *
from QuantumUtil import *
from QuantumImageEncryption import *
from itertools import product


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
        self.qImage = QuantumCircuit(len(self.image[0]), len(self.image), self.color)
        position = self.qImage.qImage.xQubit + self.qImage.qImage.yQubit
        self.qImage.measure_cluster()
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                self.qImage.encodeColor(self.util.decimal_to_binary(yi, self.qImage.qImage.yQubit),
                                        self.util.decimal_to_binary(xi, self.qImage.qImage.xQubit),
                                        color)

        self.qImage.measure_cluster()
        # print(list(map(lambda x: x[::-1], self.qImage.qImage.states)))
        self.qImageArray = sorted(self.qImage.qImage.states, key=lambda x: x[:position])
        OGImageStates = self.convertImageToStatesArray(self.image)
        print("Original Image: ", OGImageStates)

        print("Quantum Image: ", self.qImageArray)
        if OGImageStates == self.qImageArray:
            print("\033[92m Picture Successfully encoded! \033[0m")
        else:
            print("\033[91m Picture not Successfully encoded! \033[0m")
        # After encoding, create key Image and encrypt the Quantum Image
        # self.qKeyImage = QuantumKeyImage(self.qImage.qImage.width, self.qImage.qImage.height, self.color)
        # self.qKeyImage.qImage.circuit.getStates()
        # self.qKeyImageArray = sorted(self.qKeyImage.qImage.circuit.states, key=lambda x: x[:position])

    def convertImageToStatesArray(self, image):
        result = []
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                result.append(self.util.decimal_to_binary(yi, self.qImage.qImage.yQubit) +
                              self.util.decimal_to_binary(xi, self.qImage.qImage.xQubit) +
                              color)
        return result

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

        print("Random Image:", )

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
            position = qImage.qImage.xQubit + qImage.qImage.yQubit
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
