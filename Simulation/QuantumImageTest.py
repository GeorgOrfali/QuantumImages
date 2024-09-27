from QuantumAlgorithm.QuantumImageCircuit import *
from Simulation.ExecutionTimeMeasurement import *
import time
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
import random
from numpy import random
import seaborn as sns


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

    def qc_bulk_linear(self, width, height, color, case, Image=[], delay=0):
        timePerGate = 486
        totalTime = 0
        IMAGE_ARRAY = []
        qImage = QuantumImageCircuit(width, height, color)
        arrivalTime = 0
        for i in range(case):
            qImage = QuantumImageCircuit(len(Image[i][0]), len(Image[i]), len(Image[i][0][0]))
            qImage.create_circuit()
            start = time.time()
            fail = False
            # ----------------Process 1: Quantum Image Encoding Start------------------
            if Image == []:
                self.encodeQuantumImage(qImage, qImage.qImage, Image, simulation=False)
            else:
                self.encodeQuantumImage(qImage, qImage.qImage, Image[i], simulation=False)
            # ----------------Process 1: Quantum Image Encoding End--------------------

            # ----------------Process 2: Quantum Image Encryption Start----------------
            self.encryptQuantumImage(qImage, False, simulation=False)
            # ----------------Process 2: Quantum Image Encryption End------------------

            timeForImage = (timePerGate * qImage.gatesAmount) / 1000000
            totalTime = totalTime + timeForImage

            rt = 0
            if hasattr(delay, "__len__"):
                rt = delay[i]
            else:
                rt = delay

            if len(IMAGE_ARRAY) == 0:
                start = 0
            else:
                start = IMAGE_ARRAY[-1]["end"]

            arrivalTime = arrivalTime + rt
            # print(arrivalTime)
            if arrivalTime < start:
                e = {"start": start, "duration": timeForImage, "end": (start + timeForImage)}
            else:
                e = {"start": arrivalTime, "duration": timeForImage, "end": (arrivalTime + timeForImage)}

            IMAGE_ARRAY.append(e)

            qImage.gatesAmount = 0

            qImage.circuit.clear()
        # print('Image Array: ', len(IMAGE_ARRAY))
        # print(IMAGE_ARRAY)
        # print()

        # print("Total Time Linear (ms): ", IMAGE_ARRAY[-1]["end"], " for ", case, " cases with", qImage.iterationAmount,      "shots")
        return {"array": IMAGE_ARRAY, "time": IMAGE_ARRAY[-1]["end"]}

    def qc_bulk_distributed(self, width, height, color, cases, Image=[], succesrate=100, delay=0):
        QC_BULK_QUEUE = []
        ENCODE_ARRAY = []
        ENCRYPT_ARRAY = []
        TELEPORT_ARRAY = []
        arrivalTime = 0
        # init Queue
        for i in range(cases):
            encode = "Encode:" + str(i) + ":"
            QC_BULK_QUEUE.append(encode)
            encrypt = "Encrypt:" + str(i) + ":"
            QC_BULK_QUEUE.append(encrypt)

        timePerGate = 486
        if Image == []:
            qImage = QuantumImageCircuit(width, height, color)
        for i, t in enumerate(QC_BULK_QUEUE):
            task = t.split(':')
            if Image != []:
                qImage = QuantumImageCircuit(len(Image[int(task[1])][0]), len(Image[int(task[1])]),
                                             len(Image[int(task[1])][0][0]))
            rt = 0
            if hasattr(delay, "__len__"):
                rt = delay[int(task[1])]
                if rt < 0:
                    rt = 0
            else:
                rt = delay

            if task[0] == 'Encode':
                qImage.create_circuit()

                if Image == []:
                    self.encodeQuantumImage(qImage, qImage.qImage, Image, simulation=False)
                else:
                    self.encodeQuantumImage(qImage, qImage.qImage, Image[int(task[1])], simulation=False)

                timeForImage = (timePerGate * qImage.gatesAmount) / 1000000
                qImage.gatesAmount = 0
                arrivalTime = arrivalTime + rt
                # print(arrivalTime)
                start = 0
                if len(ENCODE_ARRAY) != 0:
                    start = TELEPORT_ARRAY[-1]["end"]

                if arrivalTime < start:
                    e = {"start": start, "duration": timeForImage, "end": (start + timeForImage)}
                else:
                    e = {"start": arrivalTime, "duration": timeForImage, "end": (arrivalTime + timeForImage)}
                ENCODE_ARRAY.append(e)

            elif task[0] == 'Encrypt':
                success = succesrate
                if hasattr(succesrate, "__len__"):
                    success = 100 - (succesrate[int(task[1])] * 100)

                encryptResult = self.encryptQuantumImage(qImage, True, simulation=False, successrate=success)
                teleportStart = ENCODE_ARRAY[-1]["end"]
                if len(ENCRYPT_ARRAY) > 0:
                    if ENCRYPT_ARRAY[-1]["end"] > ENCODE_ARRAY[-1]["end"]:
                        teleportStart = ENCRYPT_ARRAY[-1]["end"]
                teleportDuration = (timePerGate * encryptResult["teleport"]) / 1000000
                teleport = {"start": teleportStart, "duration": teleportDuration,
                            "end": (teleportStart + teleportDuration)}
                TELEPORT_ARRAY.append(teleport)
                timeForImage = (timePerGate * qImage.gatesAmount) / 1000000
                qImage.gatesAmount = 0

                if encryptResult['failure']:

                    encode = "Encode:" + str(task[1]) + ":fail"
                    QC_BULK_QUEUE.insert(i + 1, encode)
                    encrypt = "Encrypt:" + str(task[1]) + ":fail"
                    QC_BULK_QUEUE.insert(i + 2, encrypt)
                else:

                    start = TELEPORT_ARRAY[-1]["end"]
                    e = {"start": start, "duration": timeForImage, "end": (start + timeForImage)}
                    ENCRYPT_ARRAY.append(e)

                # qImage.circuit.draw('mpl').savefig('Distribution.png')
                qImage.circuit.clear()

        print("Total Time Distributed (ms): ", ENCRYPT_ARRAY[-1]["end"], " for ", cases, " cases with",
              qImage.iterationAmount, "shots")
        return {"array": ENCRYPT_ARRAY, "time": ENCRYPT_ARRAY[-1]["end"]}

    def qc_bulk_distributed2(self, width, height, color, cases, Image=[], succesrate=100, delay=0):
        DS2_ARRAY = []
        timePerGate = 486
        for c in range(cases):
            gates = self.DS2(width, height, color, Image[c])
            timeForImage = (timePerGate * gates) / 1000000
            if len(DS2_ARRAY) == 0:
                start = 0
            else:
                start = DS2_ARRAY[-1]["end"]

            e = {'start': start, 'duration': timeForImage, 'end': start + timeForImage}
            DS2_ARRAY.append(e)

        # print("Total Time VerticalDistribution (ms): ", DS2_ARRAY[-1]['end'])
        return {'array': DS2_ARRAY, 'time': DS2_ARRAY[-1]['end']}

    def qc_bulk_ds2_comparison(self, width, height, color, cases, Images=[], successrate=100, delay=0):
        print()
        print('------------------ Calculating Total Average Difference with VerticalDistribution ',
              ': --------------------------')
        if Images == []:
            print(cases)
            if cases > 0:
                for c in range(cases):
                    Images.append(self.generate_random_image(width, height, color, True))
            else:
                cases = 2 ** (width * height * color)
                print(cases)
                for c in range(cases):
                    Images.append(self.util.generateImageColorFromDecimal(c, color, (width * height * color), width))

        ap = 0
        for image in Images:
            linear = self.qc_bulk_linear(width, height, color, 1, [image], delay=delay)
            distributed = self.qc_bulk_distributed2(width, height, color, 1, [image], succesrate=successrate,
                                                    delay=delay)
            DecreasePercent = (distributed["time"] - linear["time"]) / distributed["time"] * 100
            ap = ap + DecreasePercent

        print("Average Time VerticalDistribution: ", (ap / len(Images)))

    def qc_bulk_comparison(self, width=2, height=2, color=2, cases=2, Imgs=[], successrate=100, delay=0):
        print()
        print('------------------ Calculating Total Average Difference with ', successrate,
              ': --------------------------')
        print()
        # print(delay)
        Images = Imgs
        Averages = []
        if Images == []:
            for c in range(cases):
                Images.append(self.generate_random_image(width, height, color, True))

        linear = self.qc_bulk_linear(width, height, color, cases, Images, delay=delay)
        distributed = self.qc_bulk_distributed(width, height, color, cases, Images, succesrate=successrate, delay=delay)
        average = 0
        occurence = []
        for j, result in enumerate(linear['array']):
            difference = (result['end'] - distributed['array'][j]['end']) / result['end']
            average = average + difference
            # diffPercent = (result['end'] - distributed['array'][j]['end'])
            # keyHist = math.floor(diffPercent)
            # occurence.append(keyHist)
        average = (average / cases) * 100
        print("Total Average Difference: ", average)
        timeDiff = (linear["time"] - distributed["time"]) / linear["time"] * 100
        print("Total Time Difference: ", timeDiff)

        # with open('output.txt', 'w') as filehandle:
        #    json.dump(occurence, filehandle)
        Averages.append(average)

    def qc_bulk_all_comparison(self):
        print()
        print("Image: 2x2 and 1 Color with 20.000 Images")
        # self.qc_bulk_comparison(2, 2, 1, 20000)
        print()
        print("Image: 2x2 and 2 Color with 20.000 Images")
        # self.qc_bulk_comparison(2, 2, 2, 20000)
        print()
        print("Image: 3x2 and 2 Color with 20.000 Images")
        # self.qc_bulk_comparison(3, 2, 2, 20000)
        print()
        print("Image: 3x3 and 2 Color with 20.000 Images")
        # self.qc_bulk_comparison(3, 3, 2, 20000)
        print()
        print("Image: 3x3 and 3 Color with 20.000 Images")
        # self.qc_bulk_comparison(3, 3, 3, 20000)
        print()
        print("Image: 4x4 and 4 Color with 20.000 Images")
        # self.qc_bulk_comparison(4, 4, 4, 20000)

    def qc_bulk_mixed_comparison(self, cases):
        print()
        print('------------------ Calculating Total Average Difference: --------------------------')
        print()
        Images = []
        for c in range(cases):
            Images.append(
                self.generate_random_image(random.randint(2, 9), random.randint(2, 9), random.randint(1, 9), True))
        self.qc_bulk_comparison(cases=cases, Imgs=Images)

    def qc_bulk_mixed_failure_comparison(self, cases):
        print()
        print('------------------ Calculating Total Average Difference: --------------------------')
        print()
        Images = []
        for c in range(cases):
            Images.append(
                self.generate_random_image(random.randint(2, 4), random.randint(2, 4), random.randint(1, 4), True))
        distribution = random.exponential(size=cases, scale=0.08)
        # snsfigure = sns.displot(data=distribution, kind="kde")
        # plt.show()
        # snsfigure.savefig("distribution_failure.png")
        self.qc_bulk_comparison(cases=cases, Imgs=Images, successrate=distribution)

    def qc_bulk_mixed_rt_comparison(self, cases):
        print()
        print('------------------ Calculating Total RT Difference: --------------------------')
        print()
        Images = []
        for c in range(cases):
            Images.append(
                self.generate_random_image(random.randint(2, 9), random.randint(2, 9), random.randint(1, 9), True))
        distribution = random.exponential(size=cases, scale=32)
        snsfigure = sns.displot(data=distribution)
        snsfigure.savefig("distribution_rt.png")
        self.qc_bulk_comparison(cases=cases, Imgs=Images, successrate=100, delay=distribution)

    def CloudTestCases(self):
        API_Token = "7d9bc1cb04724f4259fae74a8ad4af41aa6fd8f6a3dbfa065ebac31b41fc4d08e67a18770cbaae4f82649e087c28dbbd0b7c98ae935911ce29d8d106f1180d79"
        simulator = "ibmq_qasm_simulator"
        realQC = "ibm_perth"
        print('Cloud Test')
        service = QiskitRuntimeService(channel="ibm_quantum", token=API_Token)
        print('API connected')
        backend = service.backend(realQC)
        print('QC choosen')
        for i in range(5):
            QImage = QuantumImageCircuit(2, 2, 1)
            Image = [['0', '0'], ['1', '0']]
            KeyImage = [['0', '0'], ['1', '0']]

            QImage.getStates(QImage.qImage)
            encodeQuantumImage(QImage, QImage.qImage, Image)

            print(self.generateKey(QImage))

            self.encryptQuantumImage(QImage)
            QImage.measureCircuit(QImage.qImage)
            sampler = Sampler(backend=backend)
            job = sampler.run(QImage.circuit, shots=16000, resilience_level=0)
            print(f"job id: {job.job_id()}")

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

            qImage.circuit.clear()
        formatTime(totalTime, "Total")

        return {"succeed:": succeed, "failed": failed}

    def getImage(self, color):
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
