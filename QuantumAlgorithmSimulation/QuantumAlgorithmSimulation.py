from numpy import random


class QuantumAlgorithmSimulation:
    qCircuit = None

    def __init__(self, qCircuit):
        self.qCircuit = qCircuit

    def checkEncryption(self, qImage, mode="normal"):
        check = self.qCircuit.qUtil.checkEncryption(qImage, self.qCircuit.qKeyImage, mode)
        print(check["result"])
        if check["success"]:
            print(self.qCircuit.qUtil.OKGREEN, " ENCRYPTION SUCCESSFULL", self.qCircuit.qUtil.ENDC)
        else:
            print(self.qCircuit.qUtil.FAIL, " ENCRYPTION FAILED", self.qCircuit.qUtil.ENDC)

    def checkEncoding(self, qImage, Image, logs=False):
        fail = True
        qImageArray = sorted(qImage.states, key=lambda x: x[:self.qCircuit.qImage.positionQubit])
        imageArray = self.qCircuit.qUtil.convertImageToStatesArray(qImage, Image)

        if imageArray <= qImageArray:
            fail = False

        if logs:
            print(self.qCircuit.qUtil.OKBLUE, "Desired Image: ", imageArray, " Actual Image: ", qImageArray,
                  self.qCircuit.qUtil.ENDC)
            self.LogFailMessage(qImage, fail)
        return fail

    def LogFailMessage(self, qImage, fail):
        logStart = self.qCircuit.qUtil.WARNING + "LOGS: "
        message = "Name: " + qImage.name + " failed: " + str(fail)
        if fail:
            print(logStart, self.qCircuit.qUtil.FAIL, message, self.qCircuit.qUtil.ENDC)
        else:
            print(logStart, self.qCircuit.qUtil.OKGREEN, message, self.qCircuit.qUtil.ENDC)

    def generateOriginalImage(self, qImage, rand=False):
        image = []
        for h in range(qImage.height):
            row = []
            for w in range(qImage.width):
                if rand:
                    row.append(self.qCircuit.qUtil.generate_random_bit_string(qImage.colorQubit))
                else:
                    cc = ""
                    for c in range(qImage.colorQubit):
                        cc = cc + '1'
                    row.append(cc)
            image.append(row)

        qImage.setImage(image)
        return image

    def encryptVertical(self, logs=False, saveCircuit=False, success=100):
        self.qCircuit.encryptVertical(success=success)
        mode = "circuit"
        if logs:
            if saveCircuit:
                self.qCircuit.getStates(self.qCircuit.qImage, allQubits=True, saveCircuit="images/Vertical/Circuit.png",mode="circuit", remove=False)
            else:
                self.qCircuit.getStates(self.qCircuit.qImage, allQubits=True, mode="circuit")
            print(self.qCircuit.qImage.states)
            self.checkEncryption(self.qCircuit.qImage)

    def encodeQuantumImage(self, qImage, Image=[], failureSimulation=False, rand=True, logs=False):
        fail = False
        if Image == []:
            Image = self.generateOriginalImage(qImage, rand)

        self.qCircuit.encodeImage(qImage, Image)
        if failureSimulation or logs:
            self.qCircuit.getStates(qImage, shots=(2**qImage.nQubit)*20)
            fail = self.checkEncoding(qImage, Image, logs)
        else:
            qImage.states = self.qCircuit.qUtil.convertImageToStatesArray(qImage, Image)

        return fail

    def generateKey(self, qImage):
        fail = False
        QuantumKeyImageResult = self.encodeQuantumImage(qImage, qImage.qKeyImage, [], rand=True)
        QKeyImageEncodeCircuit = QuantumKeyImageResult['QImageEncodeCircuit']
        if QuantumKeyImageResult['fail']:
            fail = True
        KeyImageArray = QuantumKeyImageResult['imageArray']
        return {'fail': fail, 'KeyImageArray': KeyImageArray, 'QKeyImageEncodeCircuit': QKeyImageEncodeCircuit}

    def encryptQuantumImage(self, qImageCircuit, distributed=False, logs=False, saveCircuit=False, noise=0):
        fail = False

        if distributed:
            qImageCircuit.teleport()

            qImageCircuit.encrypt(qImageCircuit.qImageTeleported)
        else:
            qImageCircuit.encrypt(qImageCircuit.qImage)
        if logs:
            print(self.qCircuit.qEncryptionGates.gatesCost)
            mode = "normal"
            QuantumImage = self.qCircuit.qImage
            if distributed:
                mode = "normal"
                self.qCircuit.qImageTeleported.image = self.qCircuit.qImage.image
                QuantumImage = self.qCircuit.qImageTeleported
            if saveCircuit:
                if distributed:
                    self.qCircuit.getStates(QuantumImage, allQubits=True, saveCircuit="images/Task/Circuit.png", remove=False)
                else:
                    self.qCircuit.getStates(QuantumImage, allQubits=True, saveCircuit="images/Normal/Circuit.png",
                                            remove=False)
            else:
                print("Mode: ", mode)
                self.qCircuit.getStates(QuantumImage, allQubits=True)

            if noise == 0.0:
                print(self.qCircuit.qImage.states)
                self.checkEncryption(QuantumImage)

        result = {'fail': fail, 'failure': False}
        return result
