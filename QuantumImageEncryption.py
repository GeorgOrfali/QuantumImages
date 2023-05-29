from QuantumImage import *
from QuantumUtil import *


class QuantumKeyImage:
    qImage = None
    util = QuantumUtil()
    circuit = None

    def __init__(self, width, height, color):
        self.qImage = QuantumImage()
        self.qImage.setCircuit(QuantumImageCircuit(width, height, color))
        self.qImage.circuit.getStates()
        self.circuit = self.qImage.circuit
        for y in range(self.qImage.circuit.height):
            for x in range(self.qImage.circuit.width):
                self.qImage.encodeColor(self.util.decimal_to_binary(x, self.qImage.circuit.xqubits),
                                        self.util.decimal_to_binary(y, self.qImage.circuit.yqubits),
                                        self.util.generate_random_bit_string(color))
