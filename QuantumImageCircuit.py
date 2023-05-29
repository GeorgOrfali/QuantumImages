import math
from qiskit import *
from qiskit_aer import Aer


class QuantumImageCircuit:
    nqubits = 0
    xqubits = 0
    yqubits = 0
    cqubits = 0

    circuit = None
    states = []
    originalImage = []

    posQubits = []
    colorQubits = []

    width = 0
    height = 0

    def __init__(self, width, height, colorQubit):
        self.cqubits = colorQubit
        qubitAmountHeight = math.ceil(math.log(height, 2))
        self.yqubits = qubitAmountHeight
        qubitAmountWidth = math.ceil(math.log(width, 2))
        self.xqubits = qubitAmountWidth
        self.nqubits = qubitAmountHeight + qubitAmountWidth + colorQubit

        self.width = width
        self.height = height

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
                self.posQubits.append(1+2 * p)

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