from QuantumCircuit import *
from QuantumUtil import *
from QuantumImageEncryption import *
from itertools import product
import time

class QuantumImageTest:
    image = []
    qImageArray = []
    qKeyImageArray = []
    qEncryptedImageArray = []
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

        creation_time_start = time.perf_counter()
        self.qImage = QuantumCircuit(len(self.image[0]), len(self.image), self.color)
        position = self.qImage.qImage.xQubit + self.qImage.qImage.yQubit
        creation_time_end = time.perf_counter()
        print(f"\033[93m The execution time for the Normal Image creation process is: {creation_time_end-creation_time_start} \033[0m")

        measuring1_time_start = time.perf_counter()
        self.qImage.measure_cluster(self.qImage.qImage)
        measuring1_time_end = time.perf_counter()
        print(f"\033[93m The execution time for the Normal Image measuring process is: {measuring1_time_end - measuring1_time_start} \033[0m")

        encoding1_time_start = time.perf_counter()
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                self.qImage.encodeColor(self.util.decimal_to_binary(yi, self.qImage.qImage.yQubit),
                                        self.util.decimal_to_binary(xi, self.qImage.qImage.xQubit),
                                        color, self.qImage.qImage)

        encoding1_time_end = time.perf_counter()
        print(f"\033[93m The execution time for the Normal Image encoding process is: {encoding1_time_end - encoding1_time_start} \033[0m")
        measuring2_time_start = time.perf_counter()
        #self.qImage.measure_cluster(self.qImage.qImage)
        self.qImage.measure_cluster_with_cloning(self.qImage.qImage)
        measuring2_time_end = time.perf_counter()
        print(f"\033[93m The execution time for the Normal Image measuring after encoding process is: {measuring2_time_end - measuring2_time_start} \033[0m")

        self.qImageArray = sorted(self.qImage.qImage.states, key=lambda x: x[:position])
        OGImageStates = self.convertImageToStatesArray(self.image)
        print("Original Image: ", OGImageStates)
        print("Quantum Image: ", self.qImageArray)
        if OGImageStates == self.qImageArray:
            print("\033[92m Picture Successfully encoded! \033[0m")
        else:
            print("\033[91m Picture not Successfully encoded! \033[0m")
        # After encoding, create key Image and encrypt the Quantum Image

        #self.qImage.measure_cluster(self.qImage.qKeyImage)
        self.qImage.measure_cluster_with_cloning(self.qImage.qKeyImage)
        randomKeyImage = self.generate_random_image(self.qImage.qKeyImage.width, self.qImage.qKeyImage.height, self.qImage.qKeyImage.colorQubit)
        for yj, height in enumerate(randomKeyImage):
            for xj, color in enumerate(height):
                self.qImage.encodeColor(self.util.decimal_to_binary(yj, self.qImage.qKeyImage.yQubit),
                                        self.util.decimal_to_binary(xj, self.qImage.qKeyImage.xQubit),
                                        color, self.qImage.qKeyImage)

        #self.qImage.measure_cluster(self.qImage.qKeyImage)
        self.qImage.measure_cluster_with_cloning(self.qImage.qKeyImage)
        self.qKeyImageArray = sorted(self.qImage.qKeyImage.states, key=lambda x: x[:position])
        print("Name: ", self.qImage.qImage.name, "States: ", self.qImage.qImage.states, " Gates: ", self.qImage.qImage.qGates.operations)
        print("Name: ", self.qImage.qImage.name, "Position Qubits: ", self.qImage.qImage.positionQubits,
              " Color Qubits: ", self.qImage.qImage.colorQubits)
        self.qImage.encrypt()
        self.qImage.measure_cluster(self.qImage.qImage)
        #self.qImage.measure_cluster_with_cloning(self.qImage.qImage)
        self.qEncryptedImageArray = sorted(self.qImage.qImage.states, key=lambda x: x[:position])
        print("Encrypted Image states: ", self.qEncryptedImageArray)
        #print("Normal Image Gates: ", self.qImage.qImage.qGates.operations)

    def convertImageToStatesArray(self, image):
        result = []
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                result.append(self.util.decimal_to_binary(yi, self.qImage.qImage.yQubit) +
                              self.util.decimal_to_binary(xi, self.qImage.qImage.xQubit) +
                              color)
        return result

    def generate_random_image(self, width, height, color):
        image = []
        self.width = width
        self.height = height
        self.color = color

        for h in range(height):
            row = []
            for w in range(width):
                row.append(self.util.generate_random_bit_string(color))
            image.append(row)

        return image

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
            position = qImage.xQubit + qImage.yQubit
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
