import math
from qiskit import *
from qiskit_aer import Aer
from QuantumImage import *
from QuantumUtil import *
import time
import numpy as np
from QuantumGates import *

class QuantumImageCircuit:
    circuitQubits = 0

    qImage = None
    qImageTeleported = None
    qKeyImage = None
    circuit = None
    qUtil = None

    def __init__(self, width, height, colorQubits):
        self.qImage = QuantumImage('Normal Image', width, height, colorQubits)
        self.qKeyImage = QuantumImage('Key Image', width, height, colorQubits)
        self.qUtil = QuantumUtil()

        self.circuitQubits = self.qImage.nQubit + self.qKeyImage.nQubit + self.qImage.nQubit * 2

        self.create_circuit()
        # print("Created Circuit with ", self.circuitQubits, " Qubits")


class QuantumImageCircuit:
    nQubit = 0
    xQubit = 0
    yQubit = 0
    colorQubit = 0
    positionQubit = 0
    width = 0
    height = 0

    countedStates = []
    states = []

    positionQubits = []
    colorQubits = []

    qGates = None
    name = ''

    def __init__(self, name, width, height, colorQubit):
        self.name = name
        self.colorQubit = colorQubit
        self.yQubit = math.ceil(math.log(height, 2))
        self.xQubit = math.ceil(math.log(width, 2))
        self.positionQubit = self.yQubit + self.xQubit
        self.nQubit = self.positionQubit + colorQubit

    def getQImage(self):
        return self.qImage

    def getCircuit(self):
        return self.circuit

    def decimal_to_binary(self, decimal, bit_length):
        binary = bin(decimal)[2:]
        padding = bit_length - len(binary)
        binary = '0' * padding + binary
        return binary

    def create_circuit(self):
        self.qImage.clear()
        self.qKeyImage.clear()
        self.circuit = QuantumCircuit(self.circuitQubits, self.circuitQubits)
        self.create_Cluster()

    def create_Cluster(self):
        self.create_Image_Cluster(self.qImage, 0)
        self.qKeyImage.clear()
        self.create_Image_Cluster(self.qKeyImage, self.qImage.nQubit)

    def create_Image_Cluster(self, image, begin):
        for i in range(begin, (begin + image.nQubit)):
            self.circuit.h(i)

        for j in range(begin, (begin + image.nQubit)):
            if j > begin:
                self.circuit.cz((j - 1), j)
        self.circuit.barrier()
        if image.colorQubit > image.positionQubit:
            for p in range(image.positionQubit):
                image.positionQubits.append(1 + 2 * p + begin)

            for c in range(image.positionQubit):
                image.colorQubits.append(2 * c + begin)

            for cp in range(image.positionQubit * 2, image.nQubit):
                image.colorQubits.append(cp + begin)
        else:
            for c in range(image.colorQubit):
                image.colorQubits.append(2 * c + begin)

            for p in range(image.colorQubit):
                image.positionQubits.append(1 + 2 * p + begin)

            for cp in range(image.colorQubit * 2, image.nQubit):
                image.positionQubits.append(cp + begin)

    def getStates(self, image, allQubits=False):
        self.measureCircuit(image, allQubits)
        simulator = Aer.get_backend('qasm_simulator')
        circ = transpile(self.circuit, simulator)
        iterationAmount = (2 ** image.positionQubit) * 20
        result = simulator.run(self.circuit, shots=iterationAmount).result()
        counts = result.get_counts(self.circuit)
        if allQubits:
            states = [key[-image.nQubit * 2:] for key in counts.keys()]
            self.removeMeasureCircuit(image, allQubits)
            return states
        else:
            image.states = [key[-image.nQubit:] for key in counts.keys()]
            self.removeMeasureCircuit(image, allQubits)
        return image.states

    def removeMeasureCircuit(self, image, allQubits=False):
        number = 2 + image.colorQubit + image.nQubit
        if allQubits:
            number = number * 2
        lenG = len(self.circuit.data) - 1
        for i in range(number):
            self.circuit.data.pop(lenG - i)

    def addHadamardBeforeMeasurement(self, image):
        for c in range(image.colorQubit):
            self.circuit.h(image.colorQubits[c])

    def addMeasureBeforeMeasurement(self, image, n):
        for c1 in range(image.colorQubit):
            self.circuit.measure(image.colorQubits[c1], n)
            n = n + 1
        for c2 in range(image.positionQubit):
            self.circuit.measure(image.positionQubits[c2], n)
            n = n + 1
        return n

    def measureCircuit(self, image, allQubits=False):
        self.circuit.barrier()
        # First add the hadamard gates to compute from diagonal to computational basis
        self.addHadamardBeforeMeasurement(image)
        if allQubits:
            if image.name == 'Normal Image':
                self.addHadamardBeforeMeasurement(self.qKeyImage)
            else:
                self.addHadamardBeforeMeasurement(self.qImage)
        self.circuit.barrier()
        # Add the measurements, first add for all colorQubits
        n = 0
        n = self.addMeasureBeforeMeasurement(image, n)
        if allQubits:
            if image.name == 'Normal Image':
                self.addMeasureBeforeMeasurement(self.qKeyImage, n)
            else:
                self.addMeasureBeforeMeasurement(self.qImage, n)

        self.circuit.barrier()
        # Display the circuit
        # print("\033[93m Thats how the Circuit Looks like, before the measurement is not removed: \033[0m")
        # print(self.circuit.draw("text"))
        # print()

    def getCurrentClusterColorBits(self, pos, image):
        for key in image.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                # print("Found:",key)
                return key[len(pos):]

    def getCurrentClusterPositionBits(self, color, image):
        for key in image.states:
            qColor = key[:len(color)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qColor == color:
                # print("Found:",key)
                return key[len(color):]

    def getCurrentClusterBits(self, pos, image):
        result = []
        for key in image.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                return key
        # return result

    def addXGatesToPos(self, pos, image, sub_circuit=None):
        numberofPQubits = len(image.positionQubits) - 1
        for i, p in enumerate(pos):
            if p == '0':
                if sub_circuit is None:
                    self.circuit.x(image.positionQubits[numberofPQubits - i])
                else:
                    sub_circuit.x(image.positionQubits[numberofPQubits - i])

    def addXGatesToColor(self, color, image):
        numberofCQubits = len(image.colorQubits) - 1
        for i, c in enumerate(color):
            if c == '0':
                self.circuit.x(image.colorQubits[numberofCQubits - i])

    def addXGatesTo2Circuits(self, pos):
        nPQubits = len(self.qImage.positionQubits) - 1
        for i, p in enumerate(pos):
            if p == '0':
                self.circuit.x(self.qImage.positionQubits[nPQubits - i])
                self.circuit.x(self.qKeyImage.positionQubits[nPQubits - i])

    def encodeColor(self, x, y, color, image):
        startIndex = len(self.circuit.data)
        self.circuit.barrier()
        pos = x + y
        curColor = self.getCurrentClusterColorBits(pos, image)
        if curColor != color:
            self.addXGatesToPos(pos, image)
            self.addColorEncodeToCircuit(curColor, image.positionQubits, image.colorQubits, color)
            self.addXGatesToPos(pos, image)
        self.circuit.barrier()
        endIndex = len(self.circuit.data)
        return {'start': startIndex, 'end': endIndex}

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, n, sub_circuit=None):
        numberOfTargetQubits = len(TargetQubits) - 1
        for i, c in enumerate(n):
            if c != CurrentQubits[i]:
                if sub_circuit is None:
                    self.circuit.h(TargetQubits[numberOfTargetQubits - i])
                    self.circuit.barrier()
                    self.circuit.mcx(ControlQubits, TargetQubits[numberOfTargetQubits - i])
                    self.circuit.barrier()
                    self.circuit.h(TargetQubits[numberOfTargetQubits - i])
                else:
                    sub_circuit.h(TargetQubits[numberOfTargetQubits - i])
                    sub_circuit.barrier()
                    sub_circuit.mcx(ControlQubits, TargetQubits[numberOfTargetQubits - i])
                    sub_circuit.barrier()
                    sub_circuit.h(TargetQubits[numberOfTargetQubits - i])

    def encrypt(self, qImage):
        startIndex = len(self.circuit.data)
        for y in range(qImage.height):
            for x in range(qImage.width):
                pos = str(self.qUtil.decimal_to_binary(y, qImage.yQubit)) + str(
                    self.qUtil.decimal_to_binary(x, qImage.xQubit))
                self.circuit.barrier()
                # self.addXGatesTo2Circuits(pos)
                # print("Encryption Pos: ", pos)
                currentColor = self.getCurrentClusterColorBits(pos, self.qKeyImage)
                # print("Encryption currentColor: ", currentColor)
                for i, c in enumerate(currentColor):
                    if c == '1':
                        targetQImage = qImage.colorQubits[qImage.colorQubit - i - 1]
                        targetQKeyImage = self.qKeyImage.colorQubits[qImage.colorQubit - i - 1]
                        for h in self.qKeyImage.colorQubits:
                            self.circuit.h(h)

                        self.addXGatesTo2Circuits(pos)
                        ControlQubits = []
                        ControlQubits = qImage.positionQubits + self.qKeyImage.positionQubits
                        ControlQubits.append(targetQKeyImage)
                        # print("Encryption ControlQubits: ", ControlQubits)
                        self.circuit.h(qImage.colorQubits[qImage.colorQubit - i - 1])
                        # self.circuit.h(self.qKeyImage.colorQubits[self.qImage.colorQubit - i - 1])
                        self.circuit.barrier()
                        self.circuit.mcx(ControlQubits, targetQImage)
                        self.circuit.barrier()
                        self.circuit.h(qImage.colorQubits[qImage.colorQubit - i - 1])
                        # self.circuit.h(self.qKeyImage.colorQubits[self.qImage.colorQubit - i - 1])

                        self.addXGatesTo2Circuits(pos)
                        for h in self.qKeyImage.colorQubits:
                            self.circuit.h(h)
                self.circuit.barrier()
        # print(self.circuit.draw('text'))
        endIndex = len(self.circuit.data)
        return {'start': startIndex, 'end': endIndex}

    def teleport(self):
        start = len(self.circuit.data)
        startIndex = self.qImage.nQubit + self.qKeyImage.nQubit
        self.circuit.barrier()
        # Add hadamard gates for the bell pair
        for h in range(startIndex, (startIndex + self.qImage.nQubit)):
            self.circuit.h(h)
            self.circuit.cnot(h, (h + self.qImage.nQubit))

        self.circuit.barrier()
        for h in range(startIndex, (startIndex + self.qImage.nQubit)):
            self.circuit.cnot(h - startIndex, h)
            self.circuit.h(h - startIndex)

        self.circuit.barrier()

        self.qImageTeleported = QuantumImage("Teleported QImage", self.qImage.width, self.qImage.height,
                                             self.qImage.colorQubit)
        self.qImageTeleported.init_teleport(startIndex + self.qImage.nQubit, startIndex + self.qImage.nQubit * 2,
                                            self.qImage.colorQubit)

        for h in range(startIndex, (startIndex + self.qImage.nQubit)):
            self.circuit.measure(h - startIndex, h - startIndex)
            self.circuit.measure(h, h)
            self.circuit.x((h + self.qImage.nQubit)).c_if(h, 1)
            self.circuit.z((h + self.qImage.nQubit)).c_if(h - startIndex, 1)

        self.circuit.barrier()

        self.getStates(self.qImageTeleported)
        # print("States Teleported: ", set(self.qImageTeleported.states))

        endIndex = len(self.circuit.data)
        return {'start': start, 'end': endIndex}
