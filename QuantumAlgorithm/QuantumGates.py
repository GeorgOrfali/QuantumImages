# This class is for tracking the Quantum Cost in order to calculate the Execution time, cost can be described as rotation in a Qubit
# Hadamard Gate = 2 cost
# X Gate = 1 cost
# CNOT = 5
# CCNOT = 13
# MCX = for every control more than CCNOT 2 CNOT are added (V-Chain) therefor = + 10 Cost
# measurement = 1 , not proved
# source: # https://d1wqtxts1xzle7.cloudfront.net/71942047/The_cost_of_quantum_gate_primitives20211008-15829-1by4mxl.pdf?1633735392=&response-content-disposition=inline%3B+filename%3DThe_cost_of_quantum_gate_primitives.pdf&Expires=1696593390&Signature=ER5gNhN-mt~4b~Cfi4rg6yH0XwN08FG5LhL0iThq8Vf2Zbf1~rc1fw-Ems58VxhrJ3VJMTTK9k3vNEX5s8sdC2MWw0HtkQ9W6RUfZgUWLXEGZ5kXmSlXKbBp9sSu6kHU4sms-SuF5jKS5nCskutHZa0hRXRXuqfW5z4ele654mbYHIU1V88sKa6yD4nOBETk7Rr8Ode7vu90VvjkNBTK2sfjDP5msEk67PkVgOTdnBT9KGI5dvhHltmr0jXW--fzs3q1tNANSKRO~RJreiFWvjgo4awSZCZ1KT7AFDJSpl4uUZRfDq4jVQsFFQ3y9BubcvGMCP0zNFHfX3D615EjTA__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA
class QuantumGates:
    gatesCost = {}
    circuit = None

    def __init__(self, circuit, qubits):
        self.gatesCost = {}
        for q in range(qubits):
            self.gatesCost[q] = 0
        self.circuit = circuit

    def getParallelMetric(self):
        return max(self.gatesCost.values())

    def getSequentialMetric(self):
        totalAmount = 0
        for gates in self.gatesCost.values():
            totalAmount = totalAmount + gates
        return totalAmount

    def h(self, targetQubit):
        self.circuit.h(targetQubit)
        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 2

    def x(self, targetQubit):
        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 1
        return self.circuit.x(targetQubit)

    def z(self, targetQubit):
        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 1
        return self.circuit.z(targetQubit)

    def measure(self, targetQubit, register):
        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 1
        self.circuit.measure(targetQubit, register)

    def cx(self, controlQubit, targetQubit):
        self.gatesCost[controlQubit] = self.gatesCost[controlQubit] + 5
        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 5
        return self.circuit.cx(controlQubit, targetQubit)

    def cz(self, controlQubit, targetQubit):
        self.gatesCost[controlQubit] = self.gatesCost[controlQubit] + 5
        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 5
        return self.circuit.cz(controlQubit, targetQubit)

    def ccx(self, controlQubits, targetQubit):
        self.circuit.ccx(controlQubits[0], controlQubits[1], targetQubit)
        for controlQubit in controlQubits:
            self.gatesCost[controlQubit] = self.gatesCost[controlQubit] + 13

        self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + 13

    def mcx(self, controlQubits, targetQubit):
        if len(controlQubits) <= 0:
            print("Error: MCX cant have 0 Control Qubits!")
        elif len(controlQubits) == 1:
            self.cx(controlQubits[0], targetQubit)
        elif len(controlQubits) == 2:
            self.ccx(controlQubits, targetQubit)
        elif len(controlQubits) > 2:
            # First calculate amount of added Control Qubits cost
            addedCQ = len(controlQubits) - 2
            totalCost = 13 + (addedCQ*10)
            # add to circuit
            self.circuit.mcx(controlQubits, targetQubit)
            for controlQubit in controlQubits:
                self.gatesCost[controlQubit] = self.gatesCost[controlQubit] + totalCost

            self.gatesCost[targetQubit] = self.gatesCost[targetQubit] + totalCost
