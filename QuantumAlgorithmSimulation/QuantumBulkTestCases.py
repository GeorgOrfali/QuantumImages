class QuantumBulkTestCases:
    SingleTestCases = None

    def __init__(self, SingleTestCases):
        self.SingleTestCases = SingleTestCases

    def NormalBulkImage(self, width, height, color, cases, rand=True, logs=False, saveCircuit=False, parallel=False):
        totalTime = 0

        for i in range(cases):
            t = self.SingleTestCases.NormalImage(width, height, color, rand=rand, logs=logs, saveCircuit=saveCircuit, parallel=parallel)
            totalTime = totalTime + t["time"]
            if logs:
                print(i,". Image Total time: ", t["time"], " Image gates amount: ", t["gates"])

        return totalTime

    def VerticalBulkImage(self, width, height, color, cases, rand=True, logs=False, saveCircuit=False):
        totalTime = 0
        for i in range(cases):
            t = self.SingleTestCases.CircuitDistribution(width, height, color, rand=rand, logs=logs, saveCircuit=saveCircuit)
            totalTime = totalTime + t["time"]
            if logs:
                print(i,". Image Total time: ", t["time"], " Image gates amount: ", t["gates"])

        return totalTime