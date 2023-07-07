from QuantumImageCircuit import *


def encodeQuantumImage(qImageCircuit, qImage, image):
    for yi, height in enumerate(image):
        for xi, color in enumerate(height):
            qImageCircuit.encodeColor(qImageCircuit.qUtil.decimal_to_binary(yi, qImage.yQubit),
                                      qImageCircuit.qUtil.decimal_to_binary(xi, qImage.xQubit),
                                      color, qImage)


def checkEncoding(qImageArray, image):
    print("Original Image: ", image)
    print("Quantum Image: ", qImageArray)
    if image == qImageArray:
        print("\033[92m Picture Successfully encoded! \033[0m")
    else:
        print("\033[91m Picture not Successfully encoded! \033[0m")


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

    def BulkTestCases(self, width, height, color, cases):
        succeed = 0
        failed = 0
        for i in range(cases):
            fail = False
            qImage = QuantumImageCircuit(width, height, color)
            Image = self.generate_random_image(width, height, color)
            qImage.getStates(qImage.qImage)
            encodeQuantumImage(qImage, qImage.qImage, Image)
            qImage.getStates(qImage.qImage)

            position = qImage.qImage.xQubit + qImage.qImage.yQubit
            qImageArray = sorted(qImage.qImage.states, key=lambda x: x[:position])
            imageArray = self.convertImageToStatesArray(qImage, Image)
            #print(qImageArray)
            #print(imageArray)
            if qImageArray != imageArray:
                fail = True

            qImage.getStates(qImage.qKeyImage)
            keyImage = self.generate_random_image(width, height, color)
            encodeQuantumImage(qImage, qImage.qKeyImage, keyImage)
            qImage.getStates(qImage.qKeyImage)

            qKeyImageArray = sorted(qImage.qKeyImage.states, key=lambda x: x[:position])
            KeyImageArray = self.convertImageToStatesArray(qImage, keyImage)
            #print(qKeyImageArray)
            #print(KeyImageArray)
            if qKeyImageArray != KeyImageArray:
                fail = True

            qImage.encrypt()
            qImage.qImage.states = []
            qImage.getStates(qImage.qImage)
            qEncryptedImageArray = sorted(qImage.qImage.states, key=lambda x: x[:position])
            EncryptedImage = self.generate_encrypted_Image(imageArray, KeyImageArray, position)
            #print(qEncryptedImageArray)
            #print(EncryptedImage)
            if qEncryptedImageArray != EncryptedImage:
                fail = True

            if fail:
                failed = failed + 1
            else:
                succeed = succeed + 1
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

        self.qImage.encrypt()
        self.qImage.qImage.states = []
        self.qImage.getStates(self.qImage.qImage)
        self.qEncryptedImageArray = sorted(self.qImage.qImage.states, key=lambda x: x[:position])
        self.qImage.getStates(self.qImage.qKeyImage)
        print()
        print("\033[93m Encrypted Image: \033[0m", sorted(self.qImage.qImage.states, key=lambda x: x[:position]))
        print()
        print("\033[93m Encrypted Key Image: \033[0m", sorted(self.qImage.qKeyImage.states, key=lambda x: x[:position]))
        print()
        print("\033[93m All Qubits in the circuit: \033[0m", sorted(self.qImage.getStates(self.qImage.qImage, allQubits=True), key=lambda x: x[:position]))
        print()
        # self.qImage.encrypt()
        # self.qImage.getStates(self.qImage.qImage)
        # print("Decrypted: ", sorted(self.qImage.qImage.states, key=lambda x: x[:position]))
        #self.generate_encrypted_Image()

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
