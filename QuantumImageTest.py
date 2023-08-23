from QuantumImageCircuit import *
from DistributedQuantumImageCircuit import *
import time
from multiprocessing import Queue, Process, Manager
from multiprocessing.managers import BaseManager
import queue
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit import *


def encodeQuantumImage(qImageCircuit, qImage, image):
    startIndex = len(qImageCircuit.getCircuit().data)
    for yi, height in enumerate(image):
        for xi, color in enumerate(height):
            qImageCircuit.encodeColor(qImageCircuit.decimal_to_binary(yi, qImage.yQubit),
                                      qImageCircuit.decimal_to_binary(xi, qImage.xQubit),
                                      color, qImage)
    endIndex = len(qImageCircuit.getCircuit().data)
    return {'start': startIndex, 'end': endIndex}


def checkEncoding(qImageArray, image):
    # print("Original Image: ", image)
    # print("Quantum Image: ", qImageArray)
    if image == qImageArray:
        # print("\033[92m Picture Successfully encoded! \033[0m")
        return True
    else:
        # print("\033[91m Picture not Successfully encoded! \033[0m")
        return False


def checkEncryption(qEncryptedImageArray):
    return False


def formatTime(timeTook, total):
    hours, rem = divmod(timeTook, 3600)
    minutes, seconds = divmod(rem, 60)
    print("\033[93m ", total,
          "Execution time: \033[0m {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


def clearCircuit(qImageCircuit, QImageEncodeCircuit, QKeyImageEncodeCircuit, QImageEncryptCircuit,
                 QImageTeleportedCircuit=None):
    qImageCircuit.circuit.data = qImageCircuit.circuit.data[
                                 :QImageEncryptCircuit['start']] + qImageCircuit.circuit.data[
                                                                   QImageEncryptCircuit['end']:]
    if QImageTeleportedCircuit is not None:
        qImageCircuit.circuit.data = qImageCircuit.circuit.data[
                                     :QImageTeleportedCircuit['start']] + qImageCircuit.circuit.data[
                                                                          QImageTeleportedCircuit['end']:]

    qImageCircuit.circuit.data = qImageCircuit.circuit.data[
                                 :(QKeyImageEncodeCircuit['start'])] + qImageCircuit.circuit.data[
                                                                       (QKeyImageEncodeCircuit['end']):]

    qImageCircuit.circuit.data = qImageCircuit.circuit.data[
                                 :(QImageEncodeCircuit['start'])] + qImageCircuit.circuit.data[
                                                                    (QImageEncodeCircuit['end']):]
    qImageCircuit.circuit.data = qImageCircuit.circuit.data[:len(qImageCircuit.circuit.data) - 5]


def clearPartCircuit(qImageCircuit, QImagePart):
    qImageCircuit.circuit.data = qImageCircuit.circuit.data[
                                 :QImagePart['start']] + qImageCircuit.circuit.data[
                                                         QImagePart['end']:]

class QuantumImageTest:
    image = []
    qImageArray = []
    qKeyImageArray = []
    qEncryptedImageArray = []
    qImage = None
    width = 0
    height = 0
    color = 0
    util = QuantumUtil()
    QuantumEncodeQueue = Queue()
    QuantumEncryptQueue = Queue()
    circuits = []

    qImagePlain = Manager().dict(
        {'width': 0, 'height': 0, 'yQubit': 0, 'xQubit': 0, 'colorQubit': 0, 'positionQubit': 0,
         'nQubit': 0, 'colorQubits': [], 'positionQubits': []})

    qImageTeleported = Manager().dict(
        {'width': 0, 'height': 0, 'yQubit': 0, 'xQubit': 0, 'colorQubit': 0, 'positionQubit': 0,
         'nQubit': 0, 'colorQubits': [], 'positionQubits': []})

    qKeyImage = Manager().dict({'width': 0, 'height': 0, 'yQubit': 0, 'xQubit': 0, 'colorQubit': 0, 'positionQubit': 0,
                                'nQubit': 0, 'colorQubits': [], 'positionQubits': []})

    def BulkTestCasesDistributed(self, width, height, color, cases):
        QImageCircuit = QuantumImageCircuit(width, height, color)
        BaseManager().register('DistributedQuantumImageCircuit', DistributedQuantumImageCircuit)
        manager = BaseManager()
        manager.start()
        encodingCircuit = manager.DistributedQuantumImageCircuit()
        encodingCircuit.init(width, height, color, self.qImagePlain, self.qImageTeleported, self.qKeyImage)
        encryptCircuit = manager.DistributedQuantumImageCircuit()
        encryptCircuit.init(width, height, color, self.qImagePlain, self.qImageTeleported, self.qKeyImage)
        # self.circuits.append(manager.QuantumImageCircuit(width, height, color))
        # Initialise the Queue
        self.QuantumEncodeQueue.put(cases)

        Process1 = Process(target=self.distributedQuantumImageEncoding,
                           args=(encodingCircuit, width, height, color))

        Process2 = Process(target=self.distributedQuantumImageEncrypt,
                           args=(encryptCircuit, encodingCircuit, width, height, color))

        start = time.time()
        Process1.start()
        Process2.start()
        Process1.join()
        Process2.join()
        end = time.time()
        timeTook = end - start
        formatTime(timeTook, "Total")

    def distributedQuantumImageEncoding(self, encodeCircuit: DistributedQuantumImageCircuit, width, height, color):
        while True:
            try:
                task = self.QuantumEncodeQueue.get_nowait()
            except queue.Empty:
                pass
            else:
                if task == 0:
                    break

                keyTask = 'Key:' + str(task)
                self.QuantumEncryptQueue.put(keyTask)

                encodeCircuit.create_circuit(self.qImagePlain, self.qKeyImage,
                                             qImage=True)
                Image = self.generate_random_image(width, height, color)
                encodeCircuit.encodeQImage(self.qImagePlain, Image)
                encodeCircuit.getStates(self.qImagePlain)
                encodeCircuit.teleport(self.qImagePlain, self.qImageTeleported)
                self.qImageTeleported['states'] = self.qImagePlain['states']
                encryptTask = 'Encrypt:' + str(task)
                self.QuantumEncryptQueue.put(encryptTask)
        self.QuantumEncryptQueue.put('Done:0')

    def distributedQuantumImageEncrypt(self, encryptCircuit: DistributedQuantumImageCircuit,
                                       encodeCircuit: DistributedQuantumImageCircuit, width, height, color):
        while True:
            try:
                task = self.QuantumEncryptQueue.get_nowait().split(':')
                if task[1] == '0':
                    break
            except queue.Empty:
                pass
            else:
                if task[0] == 'Key':
                    encryptCircuit.create_circuit(self.qImagePlain, self.qKeyImage, key=True)
                    Image = self.generate_random_image(width, height, color)
                    encryptCircuit.encodeQImage(self.qKeyImage, Image)
                    encryptCircuit.getStates(self.qKeyImage)
                elif task[0] == "Encrypt":
                    encryptCircuit.combineCircuit(encodeCircuit.getCircuit())
                    qImageTeleported = dict(self.qImageTeleported)
                    qKeyImage = dict(self.qKeyImage)
                    encodeTask = int(task[1]) - 1
                    self.QuantumEncodeQueue.put(encodeTask)
                    encryptCircuit.encrypt(qImageTeleported, qKeyImage)

    def encodeQuantumImage(self, qImageCircuit, qImage, width, height, color):
        # ----------------Process 1 Start------------------
        # Encode Quantum Image
        fail = False
        Image = self.generate_random_image(width, height, color)
        qImageCircuit.getStates(qImage)
        QImageEncodeCircuit = encodeQuantumImage(qImageCircuit, qImage, Image)
        qImageCircuit.getStates(qImage)

        position = qImage.xQubit + qImage.yQubit
        qImageArray = sorted(qImage.states, key=lambda x: x[:position])
        imageArray = self.convertImageToStatesArray(qImageCircuit, Image)

        if not checkEncoding(qImageArray, imageArray):
            fail = True
        # ----------------Process 1 End------------------
        result = {'QImageEncodeCircuit': QImageEncodeCircuit, 'fail': fail, 'imageArray': imageArray}
        return result

    def generateKey(self, qImage, width, height, color):
        fail = False
        QuantumKeyImageResult = self.encodeQuantumImage(qImage, qImage.qKeyImage, width, height, color)
        QKeyImageEncodeCircuit = QuantumKeyImageResult['QImageEncodeCircuit']
        if QuantumKeyImageResult['fail']:
            fail = True
        KeyImageArray = QuantumKeyImageResult['imageArray']
        return {'fail': fail, 'KeyImageArray': KeyImageArray, 'QKeyImageEncodeCircuit': QKeyImageEncodeCircuit}

    def encryptQuantumImage(self, qImage, width, height, color, distributed=False):
        fail = False
        Key = self.generateKey(qImage, width, height, color)
        if Key['fail']:
            fail = True
        # ----------------Process 1 End------------------
        # ----------------Process 2 Start------------------
        # Teleport Quantum Image
        QImageTeleportedCircuit = {'start': 0, 'end': 0}

        if distributed:
            QImageTeleportedCircuit = qImage.teleport()
        # ----------------Process 2 End------------------
        # ----------------Process 3 Start------------------
        # Encrypt Image
        qImage.qImage.states = []
        if distributed:
            QImageEncryptCircuit = qImage.encrypt(qImage.qImageTeleported)
        else:
            QImageEncryptCircuit = qImage.encrypt(qImage.qImage)
        qImage.getStates(qImage.qImage)
        position = qImage.qImage.xQubit + qImage.qImage.yQubit
        qEncryptedImageArray = sorted(qImage.qImage.states, key=lambda x: x[:position])
        result = {'QKeyImageEncodeCircuit': Key['QKeyImageEncodeCircuit'], 'fail': fail,
                  'KeyImageArray': Key['KeyImageArray'],
                  'QImageTeleportedCircuit': QImageTeleportedCircuit, 'QImageEncryptCircuit': QImageEncryptCircuit,
                  'qEncryptedImageArray': qEncryptedImageArray}
        return result

    def CloudTestCases(self):
        API_Token = "7d9bc1cb04724f4259fae74a8ad4af41aa6fd8f6a3dbfa065ebac31b41fc4d08e67a18770cbaae4f82649e087c28dbbd0b7c98ae935911ce29d8d106f1180d79"
        print('Cloud Test')
        service = QiskitRuntimeService(channel="ibm_quantum", token=API_Token)
        print('API connected')
        backend = service.backend("ibm_lagos")
        print('QC choosen')
        QImage = QuantumImageCircuit(2, 2, 1)
        QImage.measureCircuit(QImage.qImage)
        print(QImage.circuit.draw('text'))

        sampler = Sampler(backend=backend)
        job = sampler.run(QImage.circuit)
        print(f"job id: {job.job_id()}")
        result = job.result()
        print(f" > Quasi probability distribution: {result.quasi_dists[0]}")
        print("result: ", result)

    def BulkTestCases(self, width, height, color, cases, distributed=False):
        succeed = 0
        failed = 0
        totalTime = 0
        qImage = QuantumImageCircuit(width, height, color)
        for i in range(cases):
            qImage.create_circuit()
            start = time.time()
            fail = False
            # ----------------Process 1: Quantum Image Encoding Start------------------
            QuantumImageResult = self.encodeQuantumImage(qImage, qImage.qImage, width, height, color)
            QImageEncodeCircuit = QuantumImageResult['QImageEncodeCircuit']
            if QuantumImageResult['fail']:
                fail = True
            imageArray = QuantumImageResult['imageArray']
            # ----------------Process 1: Quantum Image Encoding End------------------
            # ----------------Process 2: Quantum Image Encryption Start------------------
            QuantumImageEncryptionResult = self.encryptQuantumImage(qImage, width, height, color, distributed)
            position = qImage.qImage.xQubit + qImage.qImage.yQubit
            EncryptedImage = self.generate_encrypted_Image(imageArray, QuantumImageEncryptionResult['KeyImageArray'],
                                                           position)

            if EncryptedImage in QuantumImageEncryptionResult['qEncryptedImageArray']:
                fail = True

            if fail:
                failed = failed + 1
            else:
                succeed = succeed + 1
            # ----------------Process 3 End------------------
            end = time.time()
            timeTook = end - start
            totalTime = totalTime + timeTook
            # formatTime(timeTook, "")
            # print(qImage.circuit.draw('text'))
            # if distributed:
            #    clearCircuit(qImage, QImageEncodeCircuit, QuantumImageEncryptionResult['QKeyImageEncodeCircuit'],
            #                 QuantumImageEncryptionResult['QImageEncryptCircuit'],
            #                 QuantumImageEncryptionResult['QImageTeleportedCircuit'])
            # else:
            #    clearCircuit(qImage, QImageEncodeCircuit, QuantumImageEncryptionResult['QKeyImageEncodeCircuit'],
            #                 QuantumImageEncryptionResult['QImageEncryptCircuit'])
            qImage.circuit.clear()
        formatTime(totalTime, "Total")
        return {"succeed:": succeed, "failed": failed}

    def TestCasesWithArrayOutput(self):
        print("Starting the Simulation!")
        self.qImage = QuantumImageCircuit(len(self.image[0]), len(self.image), self.color)

        self.qImage.getStates(self.qImage.qImage)
        encodeQuantumImage(self.qImage, self.qImage.qImage, self.image)
        self.qImage.getStates(self.qImage.qImage)

        position = self.qImage.qImage.xQubit + self.qImage.qImage.yQubit
        self.qImageArray = sorted(self.qImage.qImage.states, key=lambda x: x[:position])
        imageArray = self.convertImageToStatesArray(self.qImage, self.image)
        checkEncoding(self.qImageArray, imageArray)

        self.qImage.getStates(self.qImage.qKeyImage)
        keyImage = self.generate_random_image(len(self.image[0]), len(self.image), self.color)
        encodeQuantumImage(self.qImage, self.qImage.qKeyImage, keyImage)
        self.qImage.getStates(self.qImage.qKeyImage)

        self.qKeyImageArray = sorted(self.qImage.qKeyImage.states, key=lambda x: x[:position])

        # Teleport the Quantum Image
        self.qImage.teleport()

        self.qImage.encrypt(self.qImage.qImageTeleported)
        self.qImage.qImage.states = []
        self.qImage.getStates(self.qImage.qImage)
        self.qEncryptedImageArray = sorted(set(self.qImage.qImage.states), key=lambda x: x[:position])
        self.qImage.getStates(self.qImage.qKeyImage)
        print()
        print("\033[93m Encrypted Image: \033[0m", sorted(self.qImage.qImage.states, key=lambda x: x[:position]))
        print("\033[93m Encrypted Image Unique: \033[0m",
              set(sorted(self.qImage.qImage.states, key=lambda x: x[:position])))
        print()
        print("\033[93m Encrypted Key Image: \033[0m", sorted(self.qImage.qKeyImage.states, key=lambda x: x[:position]))
        print("\033[93m Encrypted Key Image Unique: \033[0m",
              set(sorted(self.qImage.qKeyImage.states, key=lambda x: x[:position])))
        print()
        print("\033[93m All Qubits in the circuit: \033[0m",
              sorted(self.qImage.getStates(self.qImage.qImage, allQubits=True), key=lambda x: x[:position]))
        print(self.qImage.circuit.draw('text'))
        # self.qImage.encrypt()
        # self.qImage.getStates(self.qImage.qImage)
        # print("Decrypted: ", sorted(self.qImage.qImage.states, key=lambda x: x[:position]))
        # self.generate_encrypted_Image()

    def generate_encrypted_Image(self, qImageArray, qKeyImageArray, pos):
        resultArray = []
        for i in range(len(qImageArray)):
            states = qImageArray[i][:pos]
            colorImg = qImageArray[i][pos:]
            colorKeyImg = qKeyImageArray[i][pos:]
            color = ''
            for c in range(len(colorKeyImg)):
                if colorKeyImg[c] == '1':
                    if colorImg[c] == '1':
                        color = color + '0'
                    else:
                        color = color + '1'
                else:
                    color = color + colorImg[c]
            states = states + color
            resultArray.append(states)
        return resultArray

    def convertImageToStatesArray(self, image):
        result = []
        for yi, height in enumerate(self.image):
            for xi, color in enumerate(height):
                result.append(self.util.decimal_to_binary(yi, self.qImage.qImage.yQubit) +
                              self.util.decimal_to_binary(xi, self.qImage.qImage.xQubit) +
                              color)
        return result

    def generate_random_image(self, width, height, color):
        image = []
        self.width = width
        self.height = height
        self.color = color

        for h in range(height):
            row = []
            for w in range(width):
                row.append(self.util.generate_random_bit_string(color))
            image.append(row)
        return image

    def convertImageToStatesArray(self, qImage, image):
        result = []
        for yi, height in enumerate(image):
            for xi, color in enumerate(height):
                result.append(self.util.decimal_to_binary(yi, qImage.qImage.yQubit) +
                              self.util.decimal_to_binary(xi, qImage.qImage.xQubit) +
                              color)
        return result

    def getImage(self):
        result = ""
        for row in self.image:
            result = result + "["
            for e in row:
                result = result + " " + str(e)
            result = result + " ]\n"
        return result

    def getQuantumImage(self, qImage, qImageArray):
        position = 0
        result = ""
        open = False
        if qImage is not None:
            position = qImage.xQubit + qImage.yQubit
        for i, color in enumerate(qImageArray):
            if i % position == 0:
                if not open:
                    if i == 0:
                        result = result + "["
                        open = True
                    else:
                        result = result + "]\n["
                        open = True
                elif open:
                    result = result + "]\n["
                    open = False
            result = result + " " + str(color[position:]) + " "
            if i == len(qImageArray) - 1:
                result = result + "]"
        return result
