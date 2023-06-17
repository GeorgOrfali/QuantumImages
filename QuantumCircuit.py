from netsquid.qubits import create_qubits, measure, qubitapi
from QuantumImageCircuit import *
from QuantumUtil import *
import time


class QuantumCircuit:
    qubits = []

    qImage = None
    qKeyImage = None
    qUtil = None

    workQubits = []
    workingQubits = 0

    def __init__(self, width, height, colorQubits):
        self.qImage = QuantumImageCircuit('Normal Image', width, height, colorQubits)
        self.qKeyImage = QuantumImageCircuit('Key Image', width, height, colorQubits)
        self.qUtil = QuantumUtil()

        self.workingQubits = self.qImage.positionQubit * 2 + 1
        self.circuitQubits = self.qImage.nQubit * 2 + self.workingQubits

        self.create_circuit()
        print("Created Circuit with ", self.circuitQubits, " Qubits")

    def create_circuit(self):
        self.qImage.clear()
        self.qKeyImage.clear()
        self.workQubits = []

        self.create_Cluster()
        self.create_operations_on_circuit(self.qKeyImage)
        self.create_operations_on_circuit(self.qImage)

    def create_Cluster(self):
        self.qubits = create_qubits(self.circuitQubits)
        self.create_Image_Cluster(self.qImage, 0, self.qImage.nQubit)
        self.create_Image_Cluster(self.qKeyImage, self.qImage.nQubit, self.qKeyImage.nQubit)
        if self.qKeyImage.positionQubits[-1] >= self.qKeyImage.colorQubits[-1]:
            for w in range(1, self.workingQubits):
                self.workQubits.append(self.qKeyImage.positionQubits[-1] + w)

        # print("WorkQubits: ", self.workQubits)

    def create_Image_Cluster(self, image, begin, end):
        for i, qubit in self.qUtil.enumerate(self.qubits, begin, end):
            qubitapi.operate(qubit, qubitapi.ops.H)

        for j, qubit in self.qUtil.enumerate(self.qubits, begin, end):
            if j > begin:
                qubitapi.operate([self.qubits[j - 1], self.qubits[j]], qubitapi.ops.CZ)

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
        # print("Name: ", image.name, " PositionQubits: ", image.positionQubits, " Color Qubits: ", image.colorQubits)

    def create_operations_on_circuit(self, image):
        # print("Name: ", image.name, " Operations: ", image.qGates.operations)
        if image.qGates.operations:
            for operation in image.qGates.operations:
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

        for c in image.colorQubits:
            qubitapi.operate(self.qubits[c], qubitapi.ops.H)
            # print("Hadamard on:", c)

    def measure_states(self, image):
        qubitState = ''
        # self.create_operations_on_circuit()
        orderedQubits = image.colorQubits + image.positionQubits
        for qubit in orderedQubits:
            bit = measure(self.qubits[qubit])
            qubitState = qubitState + str(bit[0])
        image.countedStates[qubitState] = image.countedStates[qubitState] + 1

    def measure_cluster(self, image):
        image.countedStates = self.qUtil.generate_binary_combinations(image.nQubit)
        # print("All Operations: \n", image.qGates.operations)
        iterationAmount = (2 ** image.positionQubit) * 10
        print(iterationAmount)
        for i in range(iterationAmount):
            # Recreate the circuit to measure it again
            print(f"Progress: {i + 1}/{iterationAmount}", end='\r')
            self.create_circuit()
            self.measure_states(image)
        # print(self.operations)
        image.countedStates = self.qUtil.remove_zero_values(image.countedStates)
        image.states = list(map(lambda x: x[::-1], image.countedStates.keys()))
        print("States: ", image.states)

    def qubitsCopy(self, qubits):
        if not qubits:
            qubits = qubitapi.create_qubits(self.circuitQubits)
            for o, q in enumerate(self.qubits):
                # print(q.qstate)
                if q.qstate.num_qubits == 1:
                    qubitapi.assign_qstate(qubits[o], q.qstate.qrepr)
                else:
                    begin = int(q.qstate.qubits[0].name.split('-')[1])
                    end = int(len(q.qstate.qubits)) + begin
                    qubitapi.assign_qstate(qubits[begin:end], q.qstate.qrepr)
            return qubits
        else:
            for o, q in enumerate(qubits):
                if q.qstate.num_qubits == 1:
                    qubitapi.assign_qstate(self.qubits[o], q.qstate.qrepr)
                else:
                    begin = int(q.qstate.qubits[0].name.split('-')[1])
                    # end = int(q.qstate.qubits[-1].name.split('-')[1]) + 1
                    end = int(len(q.qstate.qubits)) + begin
                    qubitapi.assign_qstate(self.qubits[begin:end], q.qstate.qrepr)

    def measure_cluster_with_cloning(self, image):
        image.countedStates = self.qUtil.generate_binary_combinations(image.nQubit)
        # print("All Operations: \n", image.qGates.operations)
        iterationAmount = (2 ** image.positionQubit) * 10
        print(iterationAmount)
        self.create_circuit()
        QubitsAfterOperation = []
        QubitsAfterOperation = self.qubitsCopy(QubitsAfterOperation)
        startTimer = 0
        endTimer = 0
        for i in range(iterationAmount):
            # we clone the Qubits first
            if i % 50 == 0:
                startTimer = time.perf_counter()
            self.qubits = qubitapi.create_qubits(self.circuitQubits)
            self.qubitsCopy(QubitsAfterOperation)
            self.measure_states(image)
            if i % 50 == 0:
                endTimer = time.perf_counter()
            print(
                f"Progress: {i}/{iterationAmount} time taken: {endTimer - startTimer} Predicted Overall Time: {(endTimer - startTimer) * (iterationAmount - i)}",
                end='\r')
        image.countedStates = self.qUtil.remove_zero_values(image.countedStates)
        image.states = list(map(lambda x: x[::-1], image.countedStates.keys()))
        print("States: ", image.states)

    def addXGates(self, pos, image):
        nPQubits = self.qImage.positionQubit - 1
        Gates = []
        for i, p in enumerate(pos):
            if p == '0':
                Gates.append(image.qGates.x(image.positionQubits[nPQubits - i]))
        return Gates

    def addXGatesTo2Circuits(self, pos):
        nPQubits = self.qImage.positionQubit - 1
        Gates = []
        for i, p in enumerate(pos):
            if p == '0':
                Gates.append(self.qImage.qGates.x(self.qImage.positionQubits[nPQubits - i]))
                Gates.append(self.qImage.qGates.x(self.qKeyImage.positionQubits[nPQubits - i]))
        return Gates

    def getCurrentClusterColorBits(self, pos, image):
        for key in image.states:
            qPos = key[:len(pos)]
            if qPos == pos:
                # print("Position: ", pos, "State: ", key)
                # print("Current Color: ", key[len(pos):])
                return key[len(pos):]

    def encodeColor(self, x, y, color, image):
        pos = x + y
        # print("Pos: ", pos)
        curColor = self.getCurrentClusterColorBits(pos, image)
        # print("CurColor: ", curColor)
        # print("Desired Color: ", color)
        Gates = []
        if curColor != color:
            Gates.append(self.addXGates(pos, image))
            Gates.append(self.addColorEncodeToCircuit(curColor, image.positionQubits, image.colorQubits, color, image))
            Gates.append(self.addXGates(pos, image))
        # print("Used Gates:", Gates)

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, color, image):
        numberOfTargetQubits = len(TargetQubits) - 1
        Gates = []
        for i, c in enumerate(color):
            if c != CurrentQubits[i]:
                Gates.append(image.qGates.h(TargetQubits[numberOfTargetQubits - i]))
                Gates.append(image.qGates.mcx(self.workQubits, ControlQubits, TargetQubits[numberOfTargetQubits - i]))
                Gates.append(image.qGates.h(TargetQubits[numberOfTargetQubits - i]))

        return Gates

    def encrypt(self):
        Gates = []
        for y in range(self.qImage.height):
            for x in range(self.qImage.width):
                pos = str(self.qUtil.decimal_to_binary(y, self.qImage.yQubit)) + str(
                    self.qUtil.decimal_to_binary(x, self.qImage.xQubit))
                Gates.append(self.addXGatesTo2Circuits(pos))
                currentColor = self.getCurrentClusterColorBits(pos, self.qKeyImage)
                for i, c in enumerate(currentColor):
                    # if c == '1':
                    ControlQubits = []
                    ControlQubits = self.qImage.positionQubits + self.qKeyImage.positionQubits
                    ControlQubits.append(self.qKeyImage.colorQubits[i])
                    Gates.append(self.qImage.qGates.h(self.qImage.colorQubits[i]))
                    Gates.append(self.qImage.qGates.mcx(self.workQubits, ControlQubits, self.qImage.colorQubits[i]))
                    Gates.append(self.qImage.qGates.h(self.qImage.colorQubits[i]))

                Gates.append(self.addXGatesTo2Circuits(pos))
                Gates.append("\n")

        # print("Gates used for Encryption: ")
        # for element in Gates:
        #    if '\n' in element:
        #        print(element)
        #    else:
        #        print(element, end='')
