from qiskit import *
from QuantumAlgorithm.QuantumImage import *
from QuantumAlgorithm.QuantumUtil import *
from QuantumAlgorithm.QuantumMeasurement import *
from QuantumAlgorithm.QuantumGates import *


class QuantumImageCircuit:
    circuitQubits = 0

    classicalRegister = []

    qImage = None
    qImageTeleported = None
    qKeyImage = None
    circuit = None
    qUtil = None
    qMeasure = None
    gatesAmount = 0
    iterationAmount = 0
    qClusterGates = None
    qEncodingGates = None
    qTeleportGates = None
    qEncryptionGates = None
    noise = False

    def __init__(self, width, height, colorQubits, noise=False, distribution2=False, distributed=False):
        self.noise = noise
        self.qImage = QuantumImage('Normal Image', width, height, colorQubits)
        self.qKeyImage = QuantumImage('Key Image', width, height, colorQubits)
        self.qUtil = QuantumUtil()
        if distribution2:
            self.circuitQubits = self.qImage.nQubit + self.qKeyImage.nQubit + 3
        else:
            # 4 times because : 1 QuantumImage, 1 Quantum key, 1 Quantum Channel for teleportation, 1 Receiver
            self.circuitQubits = self.qImage.nQubit * 3 + self.qKeyImage.nQubit
        # self.circuitQubits = self.qImage.nQubit + self.qKeyImage.nQubit + self.qImage.nQubit * 2
        self.create_circuit(distribution2)

    def getQImage(self):
        return self.qImage

    def getCircuit(self):
        return self.circuit

    def create_circuit(self, distribution2=False):
        self.qImage.clear()
        self.qKeyImage.clear()

        if distribution2:
            self.circuit = QuantumCircuit(QuantumRegister(self.circuitQubits, "q"))
            for cr in range(self.circuitQubits):
                self.classicalRegister.append(ClassicalRegister(1, ("c"+str(cr))))
                self.circuit.add_register(self.classicalRegister[cr])

        else:
            self.circuit = QuantumCircuit(QuantumRegister(self.circuitQubits, "q"), ClassicalRegister(self.circuitQubits, "c"))

        self.qMeasure = QuantumMeasurement(self, self.qUtil, self.circuit, self.qImage, self.qKeyImage, self.classicalRegister)
        # Initiate the Quantum cost counter
        self.qClusterGates = QuantumGates(self.circuit, self.circuitQubits)
        self.qEncodingGates = QuantumGates(self.circuit, self.circuitQubits)
        self.qTeleportGates = QuantumGates(self.circuit, self.circuitQubits)
        self.qEncryptionGates = QuantumGates(self.circuit, self.circuitQubits)

        self.create_Cluster(distribution2)

    def create_Cluster(self, distribution2=False):
        self.create_Image_Cluster(self.qImage, 0)
        self.qKeyImage.clear()
        if distribution2:
            start = self.qImage.nQubit + 3
        else:
            start = self.qImage.nQubit
        self.create_Image_Cluster(self.qKeyImage, start)

    def create_Image_Cluster(self, image, begin):
        for i in range(begin, (begin + image.nQubit)):
            self.qClusterGates.h(i)

        for j in range(begin, (begin + image.nQubit)):
            if j > begin:
                self.qClusterGates.cz((j - 1), j)
        self.circuit.barrier()
        if image.colorQubit > image.positionQubit:
            for p in range(image.positionQubit):
                image.positionQubits.append(1 + 2 * p + begin)

            for c in range(image.positionQubit):
                image.colorQubits.append(2 * c + begin)

            for cp in range(image.positionQubit * 2, image.nQubit):
                image.colorQubits.append(cp + begin)

            for hp in image.positionQubits:
                self.qClusterGates.h(hp)
        else:
            for c in range(image.colorQubit):
                image.colorQubits.append(2 * c + begin)

            for p in range(image.colorQubit):
                image.positionQubits.append(1 + 2 * p + begin)

            for cp in range(image.colorQubit * 2, image.nQubit):
                image.positionQubits.append(cp + begin)

    def getNoise(self,  currentCircuit, desiredCircuit, allQubits=False, noise=0.5, model="bitflip", remove=True, mode="normal"):
        self.qMeasure.getNoise(currentCircuit, desiredCircuit, allQubits=allQubits, noise=noise, model=model, remove=remove, mode=mode)

    def getStates(self, image, allQubits=False, saveCircuit="", remove=True, shots=8024, mode="normal"):
        self.qMeasure.getStates(self, image, allQubits=allQubits, remove=remove, shots=shots, mode=mode)
        if saveCircuit != "":
            self.circuit.draw("mpl").savefig(saveCircuit)

    def addXGatesToPos(self, pos, image, gates):
        numberofPQubits = len(image.positionQubits) - 1
        for i, p in enumerate(pos):
            if p == '0':
                gates.x(image.positionQubits[numberofPQubits - i])

    def addXGatesToColor(self, color, image, gates):
        numberofCQubits = len(image.colorQubits) - 1
        for i, c in enumerate(color):
            if c == '0':
                gates.x(image.colorQubits[numberofCQubits - i])

    def addXGatesTo2Circuits(self, qImage, pos, gates):
        nPQubits = len(qImage.positionQubits) - 1
        for i, p in enumerate(pos):
            if p == '0':
                gates.x(qImage.positionQubits[nPQubits - i])
                gates.x(self.qKeyImage.positionQubits[nPQubits - i])
                self.gatesAmount = self.gatesAmount + 2

    def encodeImage(self, qImage, image):
        self.getStates(qImage,shots=(2**qImage.nQubit)*20)
        for yi, height in enumerate(image):
            for xi, color in enumerate(height):
                self.encodePixelColor(self.qUtil.decimal_to_binary(yi, qImage.yQubit),
                                      self.qUtil.decimal_to_binary(xi, qImage.xQubit),
                                      color, qImage)

    def encodePixelColor(self, x, y, color, qimage):
        self.circuit.barrier()
        pos = x + y
        curColor = self.qUtil.getCurrentClusterColorBits(pos, qimage)
        if curColor != color:
            self.addColorEncodeToCircuit(curColor, qimage.positionQubits, qimage.colorQubits, color, pos, qimage)
        self.circuit.barrier()

    def addColorEncodeToCircuit(self, CurrentQubits, ControlQubits, TargetQubits, n, pos, qImage):
        numberOfTargetQubits = len(TargetQubits) - 1
        for i, c in enumerate(n):
            if c != CurrentQubits[i]:
                self.addXGatesToPos(pos, qImage, self.qEncodingGates)
                self.qEncodingGates.h(TargetQubits[numberOfTargetQubits - i])
                self.qEncodingGates.mcx(ControlQubits, TargetQubits[numberOfTargetQubits - i])
                self.qEncodingGates.h(TargetQubits[numberOfTargetQubits - i])
                self.circuit.barrier()
                self.addXGatesToPos(pos, qImage, self.qEncodingGates)

    def circuitTeleport(self):
        # Teleport the qubit from the key
        # build receiver
        self.qTeleportGates.h(self.qImage.nQubit + 1)
        self.qTeleportGates.cx(self.qImage.nQubit + 1, self.qImage.nQubit)

        # build sender
        self.qTeleportGates.cx(self.qImage.nQubit + 2, self.qImage.nQubit + 1)
        self.qTeleportGates.h(self.qImage.nQubit + 2)

        # measurement
        self.circuit.barrier()
        # self.qTeleportGates.measure(self.qImage.nQubit + 1, self.classicalRegister[0])
        # self.qTeleportGates.measure(self.qImage.nQubit + 2, self.classicalRegister[1])
        self.qTeleportGates.measure(self.qImage.nQubit + 1, self.qImage.nQubit + 1)
        self.qTeleportGates.measure(self.qImage.nQubit + 2, self.qImage.nQubit + 2)
        self.circuit.barrier()

        # operations after teleport on receiver
        # self.qTeleportGates.x(self.qImage.nQubit + 1)
        self.qTeleportGates.x(self.qImage.nQubit).c_if(self.qImage.nQubit + 1, 1)
        self.qTeleportGates.z(self.qImage.nQubit).c_if(self.qImage.nQubit + 2, 1)
        # self.qTeleportGates.x(self.qImage.nQubit).c_if(self.classicalRegister[0], 1)
        # self.qTeleportGates.z(self.qImage.nQubit).c_if(self.classicalRegister[1], 1)
        # self.qTeleportGates.cx(self.qImage.nQubit + 1, self.qImage.nQubit).c_if(self.qImage.nQubit + 1, 1)
        # self.qTeleportGates.cz(self.circuitQubits - 1, self.qImage.nQubit).c_if(self.circuitQubits - 1, 1)
        # self.qTeleportGates.measure(self.qImage.nQubit, self.qImage.nQubit)
        self.circuit.barrier()
    def encryptVertical(self, success=100):
        for y in range(self.qImage.height):
            for x in range(self.qImage.width):
                pos = str(self.qUtil.decimal_to_binary(y, self.qImage.yQubit)) + str(
                    self.qUtil.decimal_to_binary(x, self.qImage.xQubit))
                self.circuit.barrier()
                currentColor = self.qUtil.getCurrentClusterColorBits(pos, self.qKeyImage)
                for i, c in enumerate(currentColor):
                    if c == '1':
                        targetQImage = self.qImage.colorQubits[self.qImage.colorQubit - i - 1]
                        targetQKeyImage = self.circuitQubits - self.qKeyImage.nQubit-1
                        ControlColorQKeyImage = self.qKeyImage.colorQubits[self.qImage.colorQubit - i - 1]

                        ControlQubitsQImage = self.qImage.positionQubits + [self.qImage.nQubit]
                        ControlQubitsQKeyImage = self.qKeyImage.positionQubits + [ControlColorQKeyImage]
                        # Encrypt Key Part
                        self.addXGatesToPos(pos, self.qKeyImage, self.qEncryptionGates)
                        self.qEncryptionGates.h(ControlColorQKeyImage)
                        self.qEncryptionGates.mcx(ControlQubitsQKeyImage, targetQKeyImage)
                        self.qEncryptionGates.h(ControlColorQKeyImage)
                        self.addXGatesToPos(pos, self.qKeyImage, self.qEncryptionGates)
                        self.circuit.barrier()

                        self.circuitTeleport()
                        if success < 100:
                            failure = 100 - success
                            while random.randint(0, 100) <= failure:
                                self.circuitTeleport()

                        # Encrypt Image Part
                        #self.qTeleportGates.h(self.qImage.nQubit)
                        self.addXGatesToPos(pos, self.qImage, self.qEncryptionGates)
                        self.qEncryptionGates.h(targetQImage)
                        self.qEncryptionGates.mcx(ControlQubitsQImage, targetQImage)
                        self.qEncryptionGates.h(targetQImage)
                        self.addXGatesToPos(pos, self.qImage, self.qEncryptionGates)
                        self.circuit.barrier()

                        # Reset Key Image Teleport Qubit, by doing the same operation again
                        self.addXGatesToPos(pos, self.qKeyImage, self.qEncryptionGates)
                        self.qEncryptionGates.h(ControlColorQKeyImage)
                        self.qEncryptionGates.mcx(ControlQubitsQKeyImage, targetQKeyImage)
                        self.qEncryptionGates.h(ControlColorQKeyImage)
                        self.addXGatesToPos(pos, self.qKeyImage, self.qEncryptionGates)
                        self.circuit.barrier()

    def encrypt(self, qImage):
        for y in range(qImage.height):
            for x in range(qImage.width):
                pos = str(self.qUtil.decimal_to_binary(y, qImage.yQubit)) + str(
                    self.qUtil.decimal_to_binary(x, qImage.xQubit))
                self.circuit.barrier()
                currentColor = self.qUtil.getCurrentClusterColorBits(pos, self.qKeyImage)
                for i, c in enumerate(currentColor):
                    if c == '1':
                        targetQImage = qImage.colorQubits[qImage.colorQubit - i - 1]
                        targetQKeyImage = self.qKeyImage.colorQubits[qImage.colorQubit - i - 1]

                        self.addXGatesTo2Circuits(qImage, pos, self.qEncryptionGates)
                        ControlQubits = []
                        ControlQubits = qImage.positionQubits + self.qKeyImage.positionQubits
                        ControlQubits.append(targetQKeyImage)
                        self.circuit.barrier()
                        self.qEncryptionGates.h(targetQKeyImage)
                        self.qEncryptionGates.h(targetQImage)
                        self.qEncryptionGates.mcx(ControlQubits, targetQImage)
                        self.qEncryptionGates.h(targetQImage)
                        self.qEncryptionGates.h(targetQKeyImage)
                        self.circuit.barrier()
                        self.addXGatesTo2Circuits(qImage, pos, self.qEncryptionGates)
                self.circuit.barrier()

    def mcx(self, ControlQubits, targetQImage):
        self.circuit.mcx(ControlQubits, targetQImage)
        if ControlQubits == 1:
            self.gatesAmount = self.gatesAmount + 5
        elif ControlQubits == 2:
            self.gatesAmount = self.gatesAmount + 13
        else:
            add = (len(ControlQubits) - 2) * 8
            self.gatesAmount = self.gatesAmount + (13 + add)

    def teleport(self):
        start = len(self.circuit.data)
        startIndex = self.qImage.nQubit + self.qKeyImage.nQubit
        self.circuit.barrier()
        # Add hadamard gates for the bell pair
        for h in range(startIndex, (startIndex + self.qImage.nQubit)):
            self.qTeleportGates.h(h)
            self.qTeleportGates.cx(h, (h + self.qImage.nQubit))

        self.circuit.barrier()
        for h in range(startIndex, (startIndex + self.qImage.nQubit)):
            self.qTeleportGates.cx(h - startIndex, h)
            self.qTeleportGates.h(h - startIndex)

        self.circuit.barrier()

        self.qImageTeleported = QuantumImage("Teleported QImage", self.qImage.width, self.qImage.height,
                                             self.qImage.colorQubit)
        self.qImageTeleported.init_teleport(startIndex + self.qImage.nQubit, startIndex + self.qImage.nQubit * 2,
                                            self.qImage.colorQubit)

        for h in range(startIndex, (startIndex + self.qImage.nQubit)):
            self.qTeleportGates.measure(h - startIndex, h - startIndex)
            self.qTeleportGates.measure(h, h)
            self.qTeleportGates.x((h + self.qImage.nQubit)).c_if(h, 1)
            self.qTeleportGates.z((h + self.qImage.nQubit)).c_if(h - startIndex, 1)

        self.circuit.barrier()

        # self.getStates(self.qImageTeleported)
        # print("States Teleported: ", set(self.qImageTeleported.states))

        endIndex = len(self.circuit.data)
        return {'start': start, 'end': endIndex}
