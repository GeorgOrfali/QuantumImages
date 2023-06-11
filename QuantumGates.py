class QuantumGates:
    operations = []

    def __init__(self):
        self.operations = []

    def h(self, targetQubit):
        self.operations.append(["H", targetQubit])
        return ["H", targetQubit]

    def x(self, targetQubit):
        self.operations.append(["X", targetQubit])
        return ["X", targetQubit]

    def cx(self, controlQubit, targetQubit):
        self.operations.append(["CX", controlQubit, targetQubit])
        return ["CX", controlQubit, targetQubit]

    def ccx(self, controlQubits, targetQubit):
        self.operations.append(["CCX", controlQubits, targetQubit])
        return ["CCX", controlQubits, targetQubit]

    def mcx(self, workQubits, controlQubits, targetQubit):
        Gates = []
        #print("Amount Control Qubits:", len(controlQubits) - 1)
        if len(controlQubits) > 2:
            countAmountOfOperations = 0
            workQubitsCounter = 0
            i = 0
            while i < len(controlQubits):
                if i == 0:
                    Gates.append(self.ccx([controlQubits[0], controlQubits[1]], workQubits[workQubitsCounter]))
                    countAmountOfOperations += 1
                    workQubitsCounter += 1
                    i += 2
                elif i == len(controlQubits) - 1:
                    # if len(controlQubits) % 2 == 0:
                    #    Gates.append(self.cx(workQubits[-1], targetQubit))
                    #    countAmountOfOperations += 1
                    #    i += 1
                    # else:
                    Gates.append(self.ccx([controlQubits[-1], workQubits[-1]], targetQubit))
                    countAmountOfOperations += 1
                    i += 1
                else:
                    Gates.append(
                        self.ccx([controlQubits[i], workQubits[workQubitsCounter - 1]], workQubits[workQubitsCounter]))
                    countAmountOfOperations += 1
                    workQubitsCounter += 1
                    i += 1

            # The second step is to debuild it
            reverse = []
            for o in range(countAmountOfOperations - 1):
                reverse.append(self.operations[-2 - o])

            for r in reverse:
                self.operations.append(r)

        else:
            Gates.append(self.ccx(controlQubits, targetQubit))

        return Gates
