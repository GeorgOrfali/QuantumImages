from netsquid.qubits import create_qubits, measure, qubitapi
from QuantumImageCircuit import *
from QuantumGates import *
from QuantumUtil import *


class QuantumCircuit:
    qubits = []

    qImage = None
    qKeyImage = None
    qGates = None
    qUtil = None

    workQubits = []
    workingQubits = 0

    def __init__(self, width, height, colorQubits):
        self.qImage = QuantumImageCircuit(width, height, colorQubits)
        self.qGates = QuantumGates()
        self.qUtil = QuantumUtil()

        if self.qImage.positionQubit > 2:
            self.workingQubits = self.qImage.positionQubit - 1
            self.circuitQubits = self.qImage.nQubit + self.workingQubits
        else:
            self.circuitQubits = self.qImage.nQubit
        self.create_circuit()
        print("Created Circuit with ", self.circuitQubits, " Qubits")

    def create_circuit(self):
        self.qImage.clear()
        self.workQubits = []

        self.create_Cluster()
        self.create_operations_on_circuit()

    def create_Cluster(self):
        self.qubits = create_qubits(self.circuitQubits)
        self.create_Image_Cluster(0, self.qImage.nQubit)
        if self.qImage.positionQubit > 2:
            if self.qImage.positionQubits[-1] >= self.qImage.colorQubits[-1]:
                for w in range(1, self.workingQubits):
                    self.workQubits.append(self.qImage.positionQubits[-1] + w)

    def create_Image_Cluster(self, begin, end):
        for i, qubit in self.qUtil.enumerate(self.qubits, begin, end):
            qubitapi.operate(qubit, qubitapi.ops.H)

        for j, qubit in self.qUtil.enumerate(self.qubits, begin, end):
            if j > 0:
                qubitapi.operate([self.qubits[j - 1], self.qubits[j]], qubitapi.ops.CZ)

        if self.qImage.colorQubit > self.qImage.positionQubit:
            for p in range(self.qImage.positionQubit):
                self.qImage.positionQubits.append(1 + 2 * p + begin)

            for c in range(self.qImage.positionQubit):
                self.qImage.colorQubits.append(2 * c + begin)

            for cp in range(self.qImage.positionQubit * 2, self.qImage.nQubit):
                self.qImage.colorQubits.append(cp + begin)
        else:
            for c in range(self.qImage.colorQubit):
                self.qImage.colorQubits.append(2 * c + begin)

            for p in range(self.qImage.colorQubit):
                self.qImage.positionQubits.append(1 + 2 * p + begin)

            for cp in range(self.qImage.colorQubit * 2, self.qImage.nQubit):
                self.qImage.positionQubits.append(cp + begin)

    def create_operations_on_circuit(self):
        if self.qGates.operations:
            for operation in self.qGates.operations:
                if operation[0] == "X":
                    qubitapi.operate(self.qubits[operation[1]], qubitapi.ops.X)
                elif operation[0] == "CCX":
                    qubitapi.operate([
                        self.qubits[operation[1][0]],
                        self.qubits[operation[1][1]],
                        self.qubits[operation[2]]
                    ], qubitapi.ops.CCX)
                elif operation[0] == "H":
                    qubitapi.operate(self.qubits[operation[1]], qubitapi.ops.H)
                elif operation[0] == "CX":
                    qubitapi.operate([self.qubits[operation[1]], self.qubits[operation[2]]], qubitapi.ops.CX)

        for c in self.qImage.colorQubits:
            qubitapi.operate(self.qubits[c], qubitapi.ops.H)

    def measure_states(self):
        qubitState = ''
        # self.create_operations_on_circuit()
        orderedQubits = self.qImage.colorQubits + self.qImage.positionQubits
        for qubit in orderedQubits:
            bit = measure(self.qubits[qubit])
            qubitState = qubitState + str(bit[0])
        self.qImage.countedStates[qubitState] = self.qImage.countedStates[qubitState] + 1

    def measure_cluster(self):
        self.qImage.countedStates = self.qUtil.generate_binary_combinations(self.qImage.nQubit)
        #print("All Operations: \n", self.qGates.operations)
        iterationAmount = (2**self.qImage.positionQubit)*5
        print(iterationAmount)
        for i in range(iterationAmount):
            # Recreate the circuit to measure it again
            self.create_circuit()
            self.measure_states()
        # print(self.operations)
        self.qImage.countedStates = self.qUtil.remove_zero_values(self.qImage.countedStates)
        self.qImage.states = list(map(lambda x: x[::-1], self.qImage.countedStates.keys()))
        print("States: ", self.qImage.states)
        #print("Cluster States: ",
        #      sorted(list(map(lambda x: x[::-1], self.qImage.states)), key=lambda x: x[:self.qImage.positionQubits]))

    def addXGates(self, pos):
        nPQubits = self.qImage.positionQubit - 1
        Gates = []
        for i, p in enumerate(pos):
            if p == '0':
                Gates.append(self.qGates.x(self.qImage.positionQubits[nPQubits - i]))
        return Gates

    def getCurrentClusterColorBits(self, pos):
        for key in self.qImage.states:
            qPos = key[:len(pos)]
            if qPos == pos:
                #print("Position: ", pos, "State: ", key)
                #print("Current Color: ", key[len(pos):])
                return key[len(pos):]

    def encodeColor(self, x, y, color):
        pos = x+y
        curColor = self.getCurrentClusterColorBits(pos)
        #print("Desired Color: ", color)
        Gates = []
        if curColor != color:
            Gates.append(self.addXGates(pos))
            Gates.append(self.addColorEncodeToCircuit(curColor, self.qImage.positionQubits, self.qImage.colorQubits, color))
            Gates.append(self.addXGates(pos))
        #print("Used Gates:", Gates)

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, color):
        numberOfTargetQubits = len(TargetQubits) - 1
        Gates = []
        for i, c in enumerate(color):
            if c != CurrentQubits[i]:
                Gates.append(self.qGates.h(TargetQubits[numberOfTargetQubits - i]))
                Gates.append(self.qGates.mcx(self.workQubits, ControlQubits, TargetQubits[numberOfTargetQubits - i]))
                Gates.append(self.qGates.h(TargetQubits[numberOfTargetQubits - i]))

        return Gates
