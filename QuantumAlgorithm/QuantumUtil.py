import random
import itertools


class QuantumUtil:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def remove_duplicates_in_dict(self, dict):
        result = {}
        for key, value in dict.items():
            key = key.replace(" ", "")
            if key not in result:
                result[key] = value
            else:
                result[key] = result[key] + value
        return result

    def generate_binary_combinations(self, n):
        binary_dict = {}
        for i in range(2 ** n):
            binary = bin(i)[2:].zfill(n)
            binary_dict[binary] = 0

        return binary_dict

    def generate_random_bit_string(self, length):
        bits = [str(random.randint(0, 1)) for _ in range(length)]
        bit_string = ''.join(bits)
        return bit_string

    def generateImageColorFromDecimal(self, decimal, color, bit_length, width):
        binary = bin(decimal)[2:]
        padding = bit_length - len(binary)
        binary = '0' * padding + binary
        Image = []
        w = 0
        row = []
        # print(len(binary), " string: ", binary)

        for b in range(0, len(binary), color):
            # print(binary[b:b+color], " w: ", w)
            if w < width:
                row.append(binary[b:b + color])
                w = w + 1
            else:
                Image.append(row)
                w = 0
                row.clear()
                row.append(binary[b:b + color])
        if len(row) > 0:
            Image.append(row)
        # print("Image: ", Image)
        return Image

    def decimal_to_binary(self, decimal, bit_length):
        binary = bin(decimal)[2:]
        padding = bit_length - len(binary)
        binary = '0' * padding + binary
        return binary

    def remove_zero_values(self, dictionary):
        return {key: value for key, value in dictionary.items() if value != 0}

    def enumerate(self, iterable, begin=0, limit=None):
        iterator = itertools.islice(iterable, begin, begin + limit) if limit is not None else iterable
        for index, item in enumerate(iterator, begin):
            yield index, item

    def getCurrentClusterColorBits(self, pos, image):
        for key in image.states:
            qPos = key[:len(pos)]
            if qPos == pos:
                return key[len(pos):]

    def getCurrentClusterPositionBits(self, color, image):
        for key in image.states:
            qColor = key[:len(color)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qColor == color:
                # print("Found:",key)
                return key[len(color):]

    def getCurrentClusterBits(self, pos, image):
        result = []
        for key in image.states:
            qPos = key[:len(pos)]
            # print('Qpos: ', qPos , " Pos: ", pos)
            if qPos == pos:
                return key
        # return result

    def convertImageToStatesArray(self, qImage, image):
        result = []
        for yi, height in enumerate(image):
            for xi, color in enumerate(height):
                result.append(self.decimal_to_binary(yi, qImage.yQubit) +
                              self.decimal_to_binary(xi, qImage.xQubit) +
                              color)
        return result

    def getStateDependingOnPosition(self, image, positionQubit, compareState):
        result = ""
        posCompareImage = compareState[:positionQubit]
        for state in image:
            # First get the position Qubits of state
            posImage = state[:positionQubit]
            # Compare position Qubits, if equal then same State is being referenced
            if posCompareImage == posImage:
                result = state
                break
        return result

    def generateOriginalImage(self, qImage, rand=False):
        image = []
        for h in range(qImage.height):
            row = []
            for w in range(qImage.width):
                if rand:
                    row.append(self.generate_random_bit_string(qImage.colorQubit))
                else:
                    cc = ""
                    for c in range(qImage.colorQubit):
                        cc = cc + '1'
                    row.append(cc)
            image.append(row)

        qImage.setImage(image)
        return image

    def generate_encrypted_Image(self, qImage, qKeyImage):
        resultArray = []
        qImageArray = qImage.image
        qKeyImageArray = qKeyImage.image
        print("QImageArray: ", qImageArray)
        print(qImage.yQubit)
        for height in range(len(qImageArray)):
            for width in range(len(qImageArray[height])):
                pos = self.decimal_to_binary(height, qImage.yQubit) +\
                      self.decimal_to_binary(width, qImage.xQubit)

                colorImg = qImageArray[height][width]
                colorKeyImg = qKeyImageArray[height][width]
                color = ''
                for c in range(len(colorKeyImg)):
                    if colorKeyImg[c] == '1':
                        if colorImg[c] == '1':
                            color = color + '0'
                        else:
                            color = color + '1'
                    else:
                        color = color + colorImg[c]

                state = pos + color
                resultArray.append(state)
        print("Generated Encrypted Image: ", resultArray)
        return resultArray

    def checkEncryption(self, qImage, qKeyImage, mode="normal"):
        EncryptedImage = self.generate_encrypted_Image(qImage, qKeyImage)

        print("Encrypted Image: ", EncryptedImage)
        success = False
        result = []
        for imageState in EncryptedImage:
            success = False
            # Get same States and add them
            keyState = self.getStateDependingOnPosition(qKeyImage.states, qKeyImage.positionQubit, imageState)
            # Check if KeyState and imageState are in result Array
            for resultState in qImage.states:
                resultState = resultState.replace(' ', '')
                if mode == "normal" or mode == "circuit":
                    checkState = keyState + imageState
                    #print("Result: ", resultState, " KeyState: ", keyState, " Image State: ", imageState)
                    if checkState == resultState[-(qImage.nQubit*2):]:
                        # Then Encryption was successfull
                        print("Result: ", resultState, " KeyState: ", keyState, " Image State: ", imageState)
                        result.append(resultState)
                        success = True
                elif mode == "job":
                    print("Result: ", resultState, " KeyState: ", keyState, " Image State: ", imageState, "Last: ", resultState[-qImage.nQubit:])
                    if imageState == resultState[-qImage.nQubit:]:
                        check = resultState.replace(resultState[-(qImage.nQubit*2):], "")
                        if keyState in check:
                            # Then Encryption was successfull
                            print("Result: ", resultState, " KeyState: ", keyState, " Image State: ", imageState)
                            result.append(resultState)
                            success = True

        return {"success": success, "result": result}