import math
import numpy as np
from QuantumGates import *


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

        self.width = width
        self.height = height

        self.qGates = QuantumGates()

    def clear(self):
        self.positionQubits = []
        self.colorQubits = []

    def getStates(self):
        return self.states
