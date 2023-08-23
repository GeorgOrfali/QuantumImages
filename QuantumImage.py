import numpy as np
import math


class QuantumImage:
    nQubit = 0
    xQubit = 0
    yQubit = 0

    colorQubit = 0
    positionQubit = 0

    width = 0
    height = 0

    states = []

    positionQubits = []
    colorQubits = []

    name = ''

    def __init__(self, name, width, height, colorQubit):
        self.name = name
        self.colorQubit = colorQubit
        self.yQubit = math.ceil(math.log(height, 2))
        self.xQubit = math.ceil(math.log(width, 2))
        self.positionQubit = self.yQubit + self.xQubit
        self.nQubit = self.positionQubit + colorQubit

        self.width = width
        self.height = height

    def init_teleport(self, start, end, colorQubit):
        self.positionQubits = []
        self.colorQubits = []
        self.colorQubit = colorQubit
        # self.yQubit =
        # self.xQubit = math.ceil(math.log(width, 2))
        self.positionQubit = end - start - colorQubit
        self.nQubit = end - start
        countPos = 0
        countColor = 0
        for q in range(start, end):
            if colorQubit > self.positionQubit:
                if q % 2 is not 0:
                    if countPos < self.positionQubit:
                        self.positionQubits.append(q)
                        countPos = countPos + 1
                    else:
                        self.colorQubits.append(q)
                else:
                    self.colorQubits.append(q)
            else:
                if q % 2 is 0:
                    if countColor < self.colorQubit:
                        self.colorQubits.append(q)
                        countColor = countColor + 1
                    else:
                        self.positionQubits.append(q)
                else:
                    self.positionQubits.append(q)

    def clear(self):
        self.positionQubits = []
        self.colorQubits = []

    def getStates(self):
        return self.states
