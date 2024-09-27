from QuantumAlgorithmSimulation.QuantumSingleTestCases import QuantumSingleTestCases
from QuantumAlgorithm.QuantumUtil import QuantumUtil
from numpy import random
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class QuantumComparedTestCases:
    SingleTestCases = None

    def __init__(self):
        self.SingleTestCases = QuantumSingleTestCases()

    def cdf(self, AverageTimes):
        plt.clf()
        s = np.sort(AverageTimes)
        # get the cdf values of y
        y = np.arange(len(AverageTimes)) / float(len(AverageTimes))
        # plotting
        plt.xlabel('Time difference of images in ms')
        plt.ylabel('Amount of occurrence')
        plt.title('CDF')

        plt.plot(s, y, marker='o')
        plt.savefig('mixed/cdf')
        print("CDF was saved as an Image file!")

    def histogram(self, AverageTimes):
        figure, ax = plt.subplots(1, 1)
        N, bins, patches = ax.hist(AverageTimes)
        percent = int(len(patches) * 0.25)

        # Set title
        ax.set_title("Histogram of average time difference")

        # adding labels
        ax.set_xlabel('Time difference of image in ms')
        ax.set_ylabel('Amount of occurence')

        #Two lines to make our compiler able to draw:
        plt.savefig('mixed/histogram')
        print("Histogram was saved as an Image file!")

    def CompareMixedFlow(self, cases, rand=False, logs=False):
        matplotlib.use('Agg')
        # totalTime = 0
        # totalAverage = 0
        # for run in range(10):
        linearTime = []
        distributedTime = []
        for i in range(cases):
            width = random.randint(2, 6)
            height = random.randint(2, 5)
            color = random.randint(1, width)
            linear = self.SingleTestCases.NormalImage(width, height, color, rand=rand, parallel=False,
                                                      logs=logs, dis2=False)
            if i == 0:
                linearTime.append(linear["time"])
            else:
                linearTime.append(linearTime[-1] + linear["time"])
            distributed = self.SingleTestCases.TaskImage(width, height, color, Image=linear["image"],
                                                         KeyImage=linear["key"],
                                                         rand=rand, logs=logs)
            distributedTime.append(distributed["partTime"])

        # Calculate total and average time
        DistributedImageTime = []
        averageTime = 0
        AverageTimes = []
        for d, dis in enumerate(distributedTime):
            # print("d: ", d , " dis: ", dis)
            start = 0
            teleport = 0
            end = 0
            if d == 0:
                teleport = dis["Encoding"] + dis["Teleportation"]
                end = teleport + dis["Encryption"]
            else:
                start = DistributedImageTime[-1]["teleport"]
                # Compare which takes longer Encoding of current Image or Encryption of before Image
                check1 = start + dis["Encoding"]
                check2 = DistributedImageTime[-1]["end"]
                if check2 >= check1:
                    teleport = check2 + dis["Teleportation"]
                else:
                    teleport = check1 + dis["Teleportation"]
                end = teleport + dis["Encryption"]
                # print("Check1: ", check1, "Check2: ", check2)
            time = {"start": start, "teleport": teleport, "end": end}
            averageTime = averageTime + ((linearTime[d] - time["end"]) / linearTime[d])
            AverageTimes.append(((linearTime[d] - time["end"])))
            # print("Dis Image: ", time)
            # print("linear Image:", linearTime[d])
            DistributedImageTime.append(time)

        # Calculate Total time difference
        totalTimeDifference = (linearTime[-1] - DistributedImageTime[-1]["end"]) / linearTime[-1]
        AverageTimeDifference = (averageTime / cases) * 100
        # print("RUN: ", run)
        print("Total Time Difference: ", (totalTimeDifference * 100))
        print("Average Time Difference: ", (AverageTimeDifference))
        self.histogram(AverageTimes)
        self.cdf(AverageTimes)
        # totalTime = totalTime + (totalTimeDifference * 100)
        # totalAverage = totalAverage + (AverageTimeDifference)

    # print("Total Averaged Time Difference: ", (totalTime/10))
    # print("Total Averaged Average Time Difference: ", (totalAverage/10))

    def CompareTaskDistribution(self, width, height, color, cases, rand=False, delay=[], logs=False, saveCircuit=False):

        linearTime = []
        distributedTime = []
        for i in range(cases):
            linear = self.SingleTestCases.NormalImage(width, height, color, rand=rand, parallel=False,
                                                      logs=logs, dis2=False)
            if i == 0:
                linearTime.append(linear["time"])
            else:
                if len(delay) == cases:
                    linearTime.append(linearTime[-1] + linear["time"] + delay[i])
                else:
                    linearTime.append(linearTime[-1] + linear["time"])
            distributed = self.SingleTestCases.TaskImage(width, height, color, Image=linear["image"],
                                                         KeyImage=linear["key"],
                                                         rand=rand, logs=logs,
                                                         saveCircuit=saveCircuit)
            distributedTime.append(distributed["partTime"])

        # Calculate total and average time
        DistributedImageTime = []
        averageTime = 0
        for d, dis in enumerate(distributedTime):
            # print("d: ", d , " dis: ", dis)
            start = 0
            teleport = 0
            end = 0
            if d == 0:
                teleport = dis["Encoding"] + dis["Teleportation"]
                end = teleport + dis["Encryption"]
            else:
                start = DistributedImageTime[-1]["teleport"]
                # Compare which takes longer Encoding of current Image or Encryption of before Image
                if len(delay) == cases:
                    check1 = start + dis["Encoding"] + delay[d]
                    check2 = DistributedImageTime[-1]["end"] + delay[d]
                else:
                    check1 = start + dis["Encoding"]
                    check2 = DistributedImageTime[-1]["end"]
                if check2 >= check1:
                    teleport = check2 + dis["Teleportation"]
                else:
                    teleport = check1 + dis["Teleportation"]
                end = teleport + dis["Encryption"]
                # print("Check1: ", check1, "Check2: ", check2)
            time = {"start": start, "teleport": teleport, "end": end}
            #print("DIS: ", dis, " TIME: ", time, " delay: ", delay[d])
            averageTime = averageTime + ((linearTime[d] - time["end"]) / linearTime[d])
            # print("Dis Image: ", time)
            # print("linear Image:", linearTime[d])
            DistributedImageTime.append(time)

        # Calculate Total time difference
        totalTimeDifference = (linearTime[-1] - DistributedImageTime[-1]["end"]) / linearTime[-1]
        AverageTimeDifference = (averageTime / cases) * 100
        print("Total Time Difference: ", (totalTimeDifference * 100))
        print("Average Time Difference: ", (AverageTimeDifference))

    def CompareCircuitDistribution(self, width, height, color, cases, rand=False, logs=False,
                                   saveCircuit=False, success=100):
        print()
        print('------------------ Calculating Total Average Difference with Circuit Distribution ',
              ': --------------------------')
        util = QuantumUtil()
        compA = 0
        maxAmount = 2 ** (width * height * color)
        if maxAmount <= cases:
            cases = maxAmount

        # create Images
        Images = []
        for c in range(cases):
            Images.append(util.generateImageColorFromDecimal(c, color, (width * height * color), width))

        for j in range(10):
            ap = 0
            for i in range(cases):
                linear = self.SingleTestCases.NormalImage(width, height, color, Image=Images[i], rand=rand,
                                                          parallel=True, logs=logs, dis2=False)
                distributed = self.SingleTestCases.CircuitDistribution(width, height, color, Image=Images[i],
                                                                       KeyImage=linear["key"],
                                                                       rand=rand, logs=logs,
                                                                       saveCircuit=saveCircuit, success=success)
                # print("Distribution: ", distributed["time"], " Linear: ", linear["time"])
                DecreasePercent = (distributed["time"] - linear["time"]) / distributed["time"] * 100
                # DecreasePercent = (linear["time"] - distributed["time"]) / linear["time"] * 100
                ap = ap + DecreasePercent
            compA = compA + (ap / cases)

            print("Average Time Circuit Distribution run: ", j, " time: ", (ap / cases))
        compA = (compA / 10)
        print("Total Average of Average time: ", compA)
