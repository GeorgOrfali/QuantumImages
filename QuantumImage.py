import numpy as np
from PIL import Image, ImageOps
import math
import random
from qiskit import *
from qiskit.quantum_info import Operator
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
from qiskit.visualization import plot_state_paulivec, plot_state_hinton
from qiskit import QuantumRegister, ClassicalRegister
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
        self.xqubits = qubitAmountWidth
        self.nqubits = qubitAmountHeight + qubitAmountWidth + colorQubit

        self.circuit = QuantumCircuit(self.nqubits, self.nqubits)

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
        if self.cqubits > (posQubits):
            for p in range(posQubits):
                self.posQubits.append(1 + 2 * p)

            for c in range(posQubits):
                self.colorQubits.append(2 * c)

            for cp in range(posQubits * 2, self.nqubits):
                self.colorQubits.append(cp)
        else:
            for c in range(self.cqubits):
                self.colorQubits.append(2 * c)

            for p in range(self.cqubits):
                self.posQubits.append(1 + 2 * p)

            for cp in range(self.cqubits * 2, self.nqubits):
                self.posQubits.append(cp)
        # Set all Colors to 0
        # for i in range(len(self.colorQubits)):
        #    cq = self.colorQubits[i]
        #    self.circuit.h(cq)
        #    self.circuit.x(cq).c_if(i,1)
        #    self.circuit.h(cq)
        print("Cluster state with", self.nqubits, "Qubits created!")
        print("---------------------------------------------------")
        print("Position Qubits: ", self.posQubits)
        print("Color Qubits: ", self.colorQubits)

    def printStates(self):
        self.states = []
        self.measureCircuit()
        simulator = Aer.get_backend('qasm_simulator')
        circ = transpile(self.circuit, simulator)
        result = simulator.run(self.circuit).result()
        counts = result.get_counts(self.circuit)
        self.states = counts
        print([n for n in self.states])
        print("---------------------------------------------------")
        self.removeMeasureCircuit()

    def removeMeasureCircuit(self):
        number = 3 + self.cqubits + self.nqubits
        lenG = len(self.circuit.data) - 1
        for i in range(number):
            self.circuit.data.pop(lenG - i)

    def measureCircuit(self):
        self.circuit.barrier()
        # First add the hadamard gates to compute from diagonal to computational basis
        for c in range(len(self.colorQubits)):
            self.circuit.h(self.colorQubits[c])

        self.circuit.barrier()
        # Add the measurements, first add for all colorQubits
        n = 0
        for c1 in range(len(self.colorQubits)):
            self.circuit.measure(self.colorQubits[c1], n)
            n = n + 1
        for c2 in range(len(self.posQubits)):
            self.circuit.measure(self.posQubits[c2], n)
            n = n + 1
        self.circuit.barrier()

    def getCurrentClusterColorBits(self, pos):
        for key in self.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                # print("Found:",key)
                return key[len(pos):]

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

    def encodeColor(self, x, y, color):
        self.circuit.barrier()
        pos = x + y
        curColor = self.getCurrentClusterColorBits(pos)
        # pos = pos[::-1]
        # color = color[::-1]
        if curColor != color:
            # First check where to put the X gates on the position qubits
            self.addXGatesToPos(pos)

            # Iterate for every Color to change
            numberOfCQubits = len(self.colorQubits) - 1
            for i, c in enumerate(color):
                if c != curColor[i]:
                    self.circuit.h(self.colorQubits[numberOfCQubits - i])
                    self.circuit.barrier()
                    self.circuit.mcx(self.posQubits, self.colorQubits[numberOfCQubits - i])
                    self.circuit.barrier()
                    self.circuit.h(self.colorQubits[numberOfCQubits - i])

            # Put the X gates again to revert the flip
            self.addXGatesToPos(pos)

        self.circuit.barrier()