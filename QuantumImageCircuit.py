import math
import numpy as np


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

    def __init__(self, width, height, colorQubit):
        self.colorQubit = colorQubit
        self.yQubit = math.ceil(math.log(height, 2))
        self.xQubit = math.ceil(math.log(width, 2))
        self.positionQubit = self.yQubit + self.xQubit
        self.nQubit = self.positionQubit + colorQubit

        self.width = width
        self.height = height

    def clear(self):
        self.positionQubits = []
        self.colorQubits = []

    def getStates(self):
        return self.states
