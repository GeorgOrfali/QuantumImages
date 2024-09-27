from QuantumAlgorithmSimulation.QuantumSingleTestCases import QuantumSingleTestCases

#This class contains all methods for executing the noise simulation for the different algorithm
class QuantumNoiseTestCases:
    SingleTestCases = None

    def __init__(self):
        self.SingleTestCases = QuantumSingleTestCases()

    def NormalImage(self, width, height, color, Image=[], rand=False, logs=False, model="bitflip", noise=0.0):

        desired = self.SingleTestCases.NormalImage(width, height, color, rand=rand, parallel=False,
                                                      logs=logs, dis2=False)
        qImageCircuitDesired = desired["qCircuit"]

        qImageCircuitCurrent = self.SingleTestCases.NormalImage(width, height, color, Image=desired["image"], rand=rand, parallel=False,
                                                      logs=logs, dis2=False)["qCircuit"]

        # Noise calculation
        qImageCircuitCurrent.getNoise(qImageCircuitCurrent, qImageCircuitDesired, allQubits=True, noise=noise, model=model, mode="normal")



    def TaskImage(self, width, height, color, Image=[], rand=False, logs=False, model="bitflip", noise=0.0):

        desired = self.SingleTestCases.NormalImage(width, height, color, rand=rand, parallel=False,
                                                      logs=logs, dis2=False)
        qImageCircuitDesired = desired["qCircuit"]

        qImageCircuitCurrent = self.SingleTestCases.TaskImage(width, height, color, Image=desired["image"], KeyImage=desired["key"], rand=rand, parallel=False,
                                                      logs=logs)["qCircuit"]

        # Noise calculation
        qImageCircuitCurrent.getNoise(qImageCircuitCurrent, qImageCircuitDesired, allQubits=True, noise=noise, model=model, mode="normal")



    def CircuitImage(self, width, height, color, Image=[], rand=False, logs=False, model="bitflip", noise=0.0):

        desired = self.SingleTestCases.NormalImage(width, height, color, rand=rand, parallel=False,
                                                      logs=logs, dis2=True)
        qImageCircuitDesired = desired["qCircuit"]

        qImageCircuitCurrent = self.SingleTestCases.CircuitDistribution(width, height, color, Image=desired["image"], KeyImage=desired["key"], rand=rand,
                                                      logs=logs)["qCircuit"]

        # Noise calculation
        qImageCircuitCurrent.getNoise(qImageCircuitCurrent, qImageCircuitDesired, allQubits=True, noise=noise, model=model, mode="circuit")