import math
from qiskit import *
from qiskit_aer import Aer


def decimal_to_binary(decimal, bit_length):
    binary = bin(decimal)[2:]
    padding = bit_length - len(binary)
    binary = '0' * padding + binary
    return binary


def convertImageToStatesArray(qImage, image):
    result = []
    for yi, height in enumerate(image):
        for xi, color in enumerate(height):
            result.append(decimal_to_binary(yi, qImage['yQubit']) +
                          decimal_to_binary(xi, qImage['xQubit']) +
                          color)
    return result


class DistributedQuantumImageCircuit:
    circuit = None
    circuitQubits = 0

    def init(self, width, height, color, qImagePlain, qImageTeleported, qKeyImage):
        self.setQImage(qImagePlain, width, height, color)
        self.setQImage(qImageTeleported, width, height, color)
        self.setQImage(qKeyImage, width, height, color)
        self.circuitQubits = qImagePlain['nQubit'] * 4

    def getCircuit(self):
        return self.circuit

    def printCircuit(self):
        print(self.circuit.draw('text'))

    def combineCircuit(self, circuit: QuantumCircuit):
        self.circuit = self.circuit.compose(circuit)

    def create_circuit(self, qImagePlain, qKeyImage, qImage=False, key=False):
        self.circuit = QuantumCircuit(self.circuitQubits, self.circuitQubits)
        if qImage:
            qubits = self.create_Image_Cluster(qImagePlain, 0)
            qImagePlain['colorQubits'] = qubits['colors']
            qImagePlain['positionQubits'] = qubits['positions']
        if key:
            qubits = self.create_Image_Cluster(qKeyImage, qImagePlain['nQubit'])
            qKeyImage['colorQubits'] = qubits['colors']
            qKeyImage['positionQubits'] = qubits['positions']

    def create_Image_Cluster(self, image, begin):
        for i in range(begin, (begin + image['nQubit'])):
            self.circuit.h(i)

        for j in range(begin, (begin + image['nQubit'])):
            if j > begin:
                self.circuit.cz((j - 1), j)
        self.circuit.barrier()
        positions = []
        colors = []
        if image['colorQubit'] > image['positionQubit']:

            for p in range(image['positionQubit']):
                positions.append(1 + 2 * p + begin)

            for c in range(image['positionQubit']):
                colors.append(2 * c + begin)

            for cp in range(image.positionQubit * 2, image['nQubit']):
                colors.append(cp + begin)

        else:
            for c in range(image['colorQubit']):
                colors.append(2 * c + begin)

            for p in range(image['colorQubit']):
                positions.append(1 + 2 * p + begin)

            for cp in range(image['colorQubit'] * 2, image['nQubit']):
                positions.append(cp + begin)

        return {'colors': colors, 'positions': positions}

    # QImage Teleport
    def teleport(self, qImagePlain, qImageTeleported):
        startIndex = qImagePlain['nQubit'] * 2
        self.circuit.barrier()
        # Add hadamard gates for the bell pair
        for h in range(startIndex, (startIndex + qImagePlain['nQubit'])):
            self.circuit.h(h)
            self.circuit.cnot(h, (h + qImagePlain['nQubit']))

        self.circuit.barrier()
        for h in range(startIndex, (startIndex + qImagePlain['nQubit'])):
            self.circuit.cnot(h - startIndex, h)
            self.circuit.h(h - startIndex)

        self.circuit.barrier()
        qubits = self.init_teleport(startIndex + qImagePlain['nQubit'], startIndex + qImagePlain['nQubit'] * 2,
                           qImagePlain['colorQubit'], qImageTeleported)

        qImageTeleported['colorQubits'] = qubits['colors']
        qImageTeleported['positionQubits'] = qubits['positions']

        for h in range(startIndex, (startIndex + qImagePlain['nQubit'])):
            self.circuit.measure(h - startIndex, h - startIndex)
            self.circuit.measure(h, h)
            self.circuit.x((h + qImagePlain['nQubit'])).c_if(h, 1)
            self.circuit.z((h + qImagePlain['nQubit'])).c_if(h - startIndex, 1)

        self.circuit.barrier()

    def init_teleport(self, start, end, colorQubit, qImageTeleported):
        qImageTeleported['positionQubit'] = end - start - colorQubit
        qImageTeleported['nQubit'] = end - start
        countPos = 0
        countColor = 0

        positions = []
        colors = []
        for q in range(start, end):
            if colorQubit > qImageTeleported['positionQubit']:
                if q % 2 != 0:
                    if countPos < qImageTeleported['positionQubit']:
                        positions.append(q)
                        countPos = countPos + 1
                    else:
                        colors.append(q)
                else:
                    colors.append(q)
            else:
                if q % 2 == 0:
                    if countColor < qImageTeleported['colorQubit']:
                        colors.append(q)
                        countColor = countColor + 1
                    else:
                        positions.append(q)
                else:
                    positions.append(q)
        return {'colors': colors, 'positions': positions}

    # QImage encryption
    def encrypt(self, qImagePlain, qKeyImage):
        for y in range(qImagePlain['height']):
            for x in range(qImagePlain['width']):
                pos = str(decimal_to_binary(y, qImagePlain['yQubit'])) + str(
                    decimal_to_binary(x, qImagePlain['xQubit']))
                self.circuit.barrier()
                currentColor = self.getCurrentClusterColorBits(pos, qKeyImage)
                for i, c in enumerate(currentColor):
                    if c == '1':
                        targetQImage = qImagePlain['colorQubits'][qImagePlain['colorQubit'] - i - 1]
                        targetQKeyImage = qKeyImage['colorQubits'][qImagePlain['colorQubit'] - i - 1]
                        for h in qKeyImage['colorQubits']:
                            self.circuit.h(h)

                        self.addXGatesTo2Circuits(pos, qImagePlain, qKeyImage)
                        ControlQubits = qImagePlain['positionQubits'] + qKeyImage['positionQubits']
                        ControlQubits.append(targetQKeyImage)
                        # print("Encryption ControlQubits: ", ControlQubits)
                        self.circuit.h(qImagePlain['colorQubits'][qImagePlain['colorQubit'] - i - 1])
                        self.circuit.barrier()
                        self.circuit.mcx(ControlQubits, targetQImage)
                        self.circuit.barrier()
                        self.circuit.h(qImagePlain['colorQubits'][qImagePlain['colorQubit'] - i - 1])

                        self.addXGatesTo2Circuits(pos, qImagePlain, qKeyImage)
                        for h in qKeyImage['colorQubits']:
                            self.circuit.h(h)
                self.circuit.barrier()

    def addXGatesTo2Circuits(self, pos, qImagePlain, qKeyImage):
        nPQubits = len(qImagePlain['positionQubits']) - 1
        for i, p in enumerate(pos):
            if p == '0':
                self.circuit.x(qImagePlain['positionQubits'][nPQubits - i])
                self.circuit.x(qKeyImage['positionQubits'][nPQubits - i])

    # QImage encoding
    def encodeQImage(self, qImage, Image):
        self.getStates(qImage)
        for yi, height in enumerate(Image):
            for xi, color in enumerate(height):
                self.encodeColor(decimal_to_binary(yi, qImage['yQubit']),
                                 decimal_to_binary(xi, qImage['xQubit']),
                                 color, qImage)

    def getCurrentClusterColorBits(self, pos, qImage):
        for key in qImage['states']:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                # print("Found:",key)
                return key[len(pos):]

    def encodeColor(self, x, y, color, qImage):
        self.circuit.barrier()
        pos = x + y
        curColor = self.getCurrentClusterColorBits(pos, qImage)
        if curColor != color:
            self.addXGatesToPos(pos, qImage)
            self.addColorEncodeToCircuit(curColor, qImage['positionQubits'], qImage['colorQubits'], color)
            self.addXGatesToPos(pos, qImage)
        self.circuit.barrier()

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, n):
        numberOfTargetQubits = len(TargetQubits) - 1
        for i, c in enumerate(n):
            if c != CurrentQubits[i]:
                self.circuit.h(TargetQubits[numberOfTargetQubits - i])
                self.circuit.barrier()
                self.circuit.mcx(ControlQubits, TargetQubits[numberOfTargetQubits - i])
                self.circuit.barrier()
                self.circuit.h(TargetQubits[numberOfTargetQubits - i])

    def addXGatesToPos(self, pos, qImage):
        numberofPQubits = len(qImage['positionQubits']) - 1
        for i, p in enumerate(pos):
            if p == '0':
                self.circuit.x(qImage['positionQubits'][numberofPQubits - i])

    # Measure QImages
    def getStates(self, qImage):
        self.measureCircuit(qImage)
        simulator = Aer.get_backend('qasm_simulator')
        circ = transpile(self.circuit, simulator)
        iterationAmount = (2 ** qImage['positionQubit']) * 20
        result = simulator.run(self.circuit, shots=iterationAmount).result()
        counts = result.get_counts(self.circuit)
        qImage['states'] = [key[-qImage['nQubit']:] for key in counts.keys()]
        qImage['states'] = sorted(set(qImage['states']), key=lambda x: x[:(qImage['xQubit'] + qImage['yQubit'])])
        self.removeMeasureCircuit(qImage)
        return qImage['states']

    def removeMeasureCircuit(self, qImage, allQubits=False):
        number = 2 + qImage['colorQubit'] + qImage['nQubit']
        if allQubits:
            number = number * 2
        lenG = len(self.circuit.data) - 1
        for i in range(number):
            self.circuit.data.pop(lenG - i)

    def addHadamardBeforeMeasurement(self, qImage):
        for c in range(qImage['colorQubit']):
            self.circuit.h(qImage['colorQubits'][c])

    def addMeasureBeforeMeasurement(self, qImage, n):
        for c1 in range(qImage['colorQubit']):
            self.circuit.measure(qImage['colorQubits'][c1], n)
            n = n + 1
        for c2 in range(qImage['positionQubit']):
            self.circuit.measure(qImage['positionQubits'][c2], n)
            n = n + 1
        return n

    def measureCircuit(self, qImage):
        self.circuit.barrier()
        # First add the hadamard gates to compute from diagonal to computational basis
        self.addHadamardBeforeMeasurement(qImage)
        self.circuit.barrier()
        # Add the measurements, first add for all colorQubits
        self.addMeasureBeforeMeasurement(qImage, 0)
        self.circuit.barrier()

    # Everything for QImage Handling
    def setQImage(self, qImage, width, height, color):
        qImage['width'] = width
        qImage['height'] = height

        qImage['yQubit'] = math.ceil(math.log(height, 2))
        qImage['xQubit'] = math.ceil(math.log(width, 2))

        qImage['colorQubit'] = color
        qImage['positionQubit'] = qImage['yQubit'] + qImage['xQubit']
        qImage['nQubit'] = qImage['positionQubit'] + qImage['colorQubit']

    def clearQImage(self, qImage):
        qImage['colorQubits'] = []
        qImage['positionQubits'] = []
