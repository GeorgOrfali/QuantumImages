import numpy as np
from PIL import Image
import math
from qiskit import *
from qiskit_aer import Aer


class QuantumImage:
    nqubits = 0
    xqubits = 0
    yqubits = 0
    cqubits = 0
    circuit = None
    states = []
    originalImage = []

    posQubits = []
    colorQubits = []

    def __init__(self, ImageUrl, colorQubit):
        image = Image.open(ImageUrl)
        imageHeight = image.height
        imageWidth = image.width
        print('Image Array Loaded: ')
        print(np.asarray(image, dtype=int))
        print("---------------------------------------------------")
        self.cqubits = colorQubit
        qubitAmountHeight = math.ceil(math.log(imageHeight, 2))
        self.yqubits = qubitAmountHeight
        qubitAmountWidth = math.ceil(math.log(imageWidth, 2))
        if (qubitAmountHeight+qubitAmountWidth) < colorQubit:
            qubitAmountWidth = qubitAmountWidth + 1

        self.xqubits = qubitAmountWidth

        self.nqubits = qubitAmountHeight + qubitAmountWidth + colorQubit

        self.circuit = QuantumCircuit(self.nqubits, self.nqubits)

    def __init__(self, array, colorQubit):
        self.cqubits = colorQubit
        qubitAmountHeight = math.ceil(math.log(len(array), 2))
        self.yqubits = qubitAmountHeight
        qubitAmountWidth = math.ceil(math.log(len(array[0]), 2))
        if (qubitAmountHeight+qubitAmountWidth) < colorQubit:
            qubitAmountWidth = qubitAmountWidth + 1
        self.xqubits = qubitAmountWidth
        self.nqubits = qubitAmountHeight + qubitAmountWidth + colorQubit

        self.circuit = QuantumCircuit(self.nqubits, self.nqubits)
        self.createCluster()

    def createCluster(self):

        for i in range(self.nqubits):
            self.circuit.h(i)

        for i in range(self.nqubits):
            if i > 0:
                self.circuit.cz(i - 1, i)
        self.circuit.barrier()
        self.posQubits = []
        self.colorQubits = []
        # create List of Color Qubits and Position Qubits
        posQubits = self.xqubits + self.yqubits
        if self.cqubits > posQubits:
            for p in range(posQubits):
                self.posQubits.append(2 * p)

            for c in range(posQubits):
                self.colorQubits.append(1+2 * c)

            for cp in range(posQubits * 2, self.nqubits):
                self.colorQubits.append(cp)
        else:
            for c in range(self.cqubits):
                self.colorQubits.append(2 * c)

            for p in range(self.cqubits):
                self.posQubits.append(1 + 2 * p)

            for cp in range(self.cqubits * 2, self.nqubits):
                self.posQubits.append(cp)

        print("Cluster state with", self.nqubits, "Qubits created!")
        print("---------------------------------------------------")
        print("Position Qubits: ", self.posQubits)
        print("Color Qubits: ", self.colorQubits)

    def getStates(self):
        self.states = []
        self.measureCircuit()
        simulator = Aer.get_backend('qasm_simulator')
        circ = transpile(self.circuit, simulator)
        result = simulator.run(self.circuit).result()
        counts = result.get_counts(self.circuit)
        self.states = counts
        self.removeMeasureCircuit()

    def printStates(self):
        print([n for n in self.states])
        print("---------------------------------------------------")

    def removeMeasureCircuit(self):
        if len(self.posQubits) >= self.cqubits:
            number = 3 + self.cqubits + self.nqubits
            lenG = len(self.circuit.data) - 1
            for i in range(number):
                self.circuit.data.pop(lenG - i)
        else:
            number = 3 + len(self.posQubits) + self.nqubits
            lenG = len(self.circuit.data) - 1
            for i in range(number):
                self.circuit.data.pop(lenG - i)

    def measureCircuit(self):
        self.circuit.barrier()
        # First add the hadamard gates to compute from diagonal to computational basis
        if len(self.posQubits) >= len(self.colorQubits):
            for c in range(len(self.colorQubits)):
                self.circuit.h(self.colorQubits[c])
        else:
            for p in range(len(self.posQubits)):
                self.circuit.h(self.posQubits[p])

        self.circuit.barrier()
        # Add the measurements, first add for all colorQubits
        n = 0
        if len(self.posQubits) >= len(self.colorQubits):
            for c1 in range(len(self.colorQubits)):
                self.circuit.measure(self.colorQubits[c1], n)
                n = n + 1
            for c2 in range(len(self.posQubits)):
                self.circuit.measure(self.posQubits[c2], n)
                n = n + 1
        else:
            for c2 in range(len(self.posQubits)):
                self.circuit.measure(self.posQubits[c2], n)
                n = n + 1
            for c1 in range(len(self.colorQubits)):
                self.circuit.measure(self.colorQubits[c1], n)
                n = n + 1
        self.circuit.barrier()

    def getCurrentClusterColorBits(self, pos):
        for key in self.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                # print("Found:",key)
                return key[len(pos):]

    def getCurrentClusterPositionBits(self, color):
        for key in self.states:
            qColor = key[:len(color)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qColor == color:
                # print("Found:",key)
                return key[len(color):]

    def getCurrentClusterBits(self, pos):
        result = []
        for key in self.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                return key
        # return result

    def addXGatesToPos(self, pos):
        numberofPQubits = len(self.posQubits) - 1
        for i, p in enumerate(pos):
            if p == '0':
                self.circuit.x(self.posQubits[numberofPQubits - i])

    def addXGatesToColor(self, color):
        numberofCQubits = len(self.colorQubits) - 1
        for i, c in enumerate(color):
            if c == '0':
                self.circuit.x(self.colorQubits[numberofCQubits - i])

    def encodeColor(self, x, y, color):
        self.circuit.barrier()
        pos = y+x
        if len(self.posQubits) >= len(self.colorQubits):
            curColor = self.getCurrentClusterColorBits(pos)
            if curColor != color:
                self.addXGatesToPos(pos)
                self.addColorEncodeToCircuit(curColor, self.posQubits, self.colorQubits, color)
                self.addXGatesToPos(pos)
        else:
            curPos = self.getCurrentClusterPositionBits(color)
            print("CurPos: ", curPos, " pos: ", pos, " color: ", color)
            if curPos != pos:
                self.addXGatesToColor(color)
                self.addColorEncodeToCircuit(curPos, self.colorQubits, self.posQubits, pos)
                self.addXGatesToColor(color)
        self.circuit.barrier()

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, n):
        numberOfTargetQubits = len(TargetQubits) - 1
        for i, c in enumerate(n):
            if c != CurrentQubits[i]:
                self.circuit.h(TargetQubits[numberOfTargetQubits - i])
                self.circuit.barrier()
                self.circuit.mcx(ControlQubits, TargetQubits[numberOfTargetQubits - i])
                self.circuit.barrier()
                self.circuit.h(TargetQubits[numberOfTargetQubits - i])
