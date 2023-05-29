import numpy as np
from PIL import Image
from QuantumImageCircuit import *


class QuantumImage:
    circuit = None

    def setCircuitWithImage(self, ImageUrl, colorQubit):
        image = Image.open(ImageUrl)
        imageHeight = image.height
        imageWidth = image.width
        print('Image Array Loaded: ')
        print(np.asarray(image, dtype=int))
        print("---------------------------------------------------")
        self.circuit = QuantumImageCircuit(imageWidth, imageHeight, colorQubit)

    def setCircuitWithArray(self, array, colorQubit):
        self.circuit = QuantumImageCircuit(len(array[0]), len(array), colorQubit)

    def setCircuit(self, quantumImageCircuit):
        self.circuit = quantumImageCircuit

    def getCurrentClusterColorBits(self, pos):
        for key in self.circuit.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                # print("Found:",key)
                return key[len(pos):]

    def getCurrentClusterPositionBits(self, color):
        for key in self.circuit.states:
            qColor = key[:len(color)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qColor == color:
                # print("Found:",key)
                return key[len(color):]

    def getCurrentClusterBits(self, pos):
        result = []
        for key in self.circuit.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                return key
        # return result

    def addXGatesToPos(self, pos):
        numberofPQubits = len(self.circuit.posQubits) - 1
        for i, p in enumerate(pos):
            if p == '0':
                self.circuit.circuit.x(self.circuit.posQubits[numberofPQubits - i])

    def addXGatesToColor(self, color):
        numberofCQubits = len(self.circuit.colorQubits) - 1
        for i, c in enumerate(color):
            if c == '0':
                self.circuit.circuit.x(self.circuit.colorQubits[numberofCQubits - i])

    def encodeColor(self, x, y, color):
        self.circuit.circuit.barrier()
        pos = y + x
        curColor = self.getCurrentClusterColorBits(pos)
        if curColor != color:
            self.addXGatesToPos(pos)
            self.addColorEncodeToCircuit(curColor, self.circuit.posQubits, self.circuit.colorQubits, color)
            self.addXGatesToPos(pos)
        self.circuit.circuit.barrier()
        # print(self.circuit.circuit.draw('text'))

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, n):
        numberOfTargetQubits = len(TargetQubits) - 1
        for i, c in enumerate(n):
            if c != CurrentQubits[i]:
                self.circuit.circuit.h(TargetQubits[numberOfTargetQubits - i])
                self.circuit.circuit.barrier()
                self.circuit.circuit.mcx(ControlQubits, TargetQubits[numberOfTargetQubits - i])
                self.circuit.circuit.barrier()
                self.circuit.circuit.h(TargetQubits[numberOfTargetQubits - i])
