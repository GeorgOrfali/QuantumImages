from QuantumAlgorithm.QuantumImageCircuit import QuantumImageCircuit
from QuantumAlgorithmSimulation.QuantumAlgorithmSimulation import *
from Simulation.ExecutionTimeMeasurement import ExecutionTimeMeasurement


class QuantumSingleTestCases:
    def __init__(self):
        pass

    def NormalImage(self, width, height, color, Image=[], rand=True, logs=False, saveCircuit=False, parallel=False, noise=0, dis2=False):

        qImageCircuit = QuantumImageCircuit(width, height, color, noise=False, distribution2=dis2)
        algorithm = QuantumAlgorithmSimulation(qImageCircuit)

        # Quantum Image
        algorithm.encodeQuantumImage(qImageCircuit.qImage, Image, rand=rand, logs=logs)

        # Quantum Key
        algorithm.encodeQuantumImage(qImageCircuit.qKeyImage, rand=rand, logs=logs)
        # Encrypt
        algorithm.encryptQuantumImage(qImageCircuit, logs=logs, saveCircuit=saveCircuit, noise=noise)
        executionTime = ExecutionTimeMeasurement(qImageCircuit)
        if parallel:
            totalTime = executionTime.getParallelTime()
        else:
            totalTime = executionTime.getSequentialTimeLinear()

        totalTime["image"] = qImageCircuit.qImage.image
        totalTime["key"] = qImageCircuit.qKeyImage.image
        totalTime["partTime"] = executionTime.getPartTime()
        totalTime["qCircuit"] = qImageCircuit
        #print(executionTime.getPartTime())
        return totalTime

    def TaskImage(self, width, height, color, rand=True, logs=False, saveCircuit=False, parallel=False, noise=0, delay=0, Image=[], KeyImage=[]):
        qImageCircuit = QuantumImageCircuit(width, height, color, noise=False)
        algorithm = QuantumAlgorithmSimulation(qImageCircuit)

        # Quantum Image
        algorithm.encodeQuantumImage(qImageCircuit.qImage, Image=Image, rand=rand, logs=logs)

        # Quantum Key
        algorithm.encodeQuantumImage(qImageCircuit.qKeyImage, Image=KeyImage, rand=rand, logs=logs)

        # Encrypt
        algorithm.encryptQuantumImage(qImageCircuit, distributed=True, logs=logs, saveCircuit=saveCircuit, noise=noise)

        executionTime = ExecutionTimeMeasurement(qImageCircuit)
        if parallel:
            totalTime = executionTime.getParallelTime()
        else:
            totalTime = executionTime.getSequentialTimeLinear()

        totalTime["image"] = qImageCircuit.qImage.image
        totalTime["key"] = qImageCircuit.qKeyImage.image
        totalTime["partTime"] = executionTime.getPartTime()
        totalTime["qCircuit"] = qImageCircuit
        return totalTime

    def CircuitDistribution(self, width, height, color, rand=True, logs=False, saveCircuit=False, success=100, Image=[], KeyImage=[]):
        qImageCircuit = QuantumImageCircuit(width, height, color, noise=False,
                                            distribution2=True, distributed=False)
        algorithm = QuantumAlgorithmSimulation(qImageCircuit)

        # Quantum Image
        algorithm.encodeQuantumImage(qImageCircuit.qImage, Image=Image, rand=rand, logs=logs)

        # Quantum Key
        algorithm.encodeQuantumImage(qImageCircuit.qKeyImage, Image=KeyImage, rand=rand, logs=logs)

        # Encrypt
        algorithm.encryptVertical(logs=logs, saveCircuit=saveCircuit, success=success)

        executionTime = ExecutionTimeMeasurement(qImageCircuit)
        totalTime = executionTime.getParallelTime()
        totalTime["qCircuit"] = qImageCircuit
        return totalTime
