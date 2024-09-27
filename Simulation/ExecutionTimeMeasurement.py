
class ExecutionTimeMeasurement:
    qImageCircuit = None
    # in nanoseconds, was extracted from IBM Cloud machine
    timePerGate = 561.778

    def __init__(self, qImageCircuit):
        self.qImageCircuit = qImageCircuit

    def getParallelTime(self):
        gates = self.qImageCircuit.qClusterGates.getParallelMetric() + \
                self.qImageCircuit.qEncodingGates.getParallelMetric() + \
                self.qImageCircuit.qTeleportGates.getParallelMetric() + \
                self.qImageCircuit.qEncryptionGates.getParallelMetric()

        timeForImage = (self.timePerGate * gates) / 1000000
        return {"time": timeForImage, "gates": gates}

    def getSequentialTimeLinear(self):
        gates = self.qImageCircuit.qClusterGates.getSequentialMetric() + \
                self.qImageCircuit.qEncodingGates.getSequentialMetric() + \
                self.qImageCircuit.qTeleportGates.getSequentialMetric() + \
                self.qImageCircuit.qEncryptionGates.getSequentialMetric()

        timeForImage = (self.timePerGate * gates) / 1000000
        return {"time": timeForImage, "gates": gates}

    def getPartTime(self):
        EncodingGates = self.qImageCircuit.qClusterGates.getSequentialMetric() + \
                        self.qImageCircuit.qEncodingGates.getSequentialMetric()
        EncodingTime = (self.timePerGate * EncodingGates) / 1000000
        TeleportationTime = (self.timePerGate * self.qImageCircuit.qTeleportGates.getSequentialMetric()) / 1000000
        EncryptionTime = (self.timePerGate * self.qImageCircuit.qEncryptionGates.getSequentialMetric()) / 1000000

        return {"Encoding": EncodingTime, "Teleportation": TeleportationTime, "Encryption": EncryptionTime}
