import ttkbootstrap as ttk
from QuantumAlgorithmSimulation.QuantumSingleTestCases import QuantumSingleTestCases
from QuantumAlgorithmSimulation.QuantumBulkTestCases import QuantumBulkTestCases
from QuantumAlgorithmSimulation.QuantumComparedTestCases import QuantumComparedTestCases
from QuantumAlgorithmSimulation.QuantumNoiseTestCases import QuantumNoiseTestCases
from threading import Thread
import time
import math
from numpy import random
import seaborn as sns


class GuiModern:
    root = None
    headline = None
    SingleTestCases = None
    NoiseTestCases = None
    BulkTestCases = None
    CompareTestCases = None
    imageOptions = None
    simulation = None

    def __init__(self, root):
        self.root = root
        ttk.Style().configure('sidebar.TButton', font=("Helvetica", 26))
        ttk.Style().configure('simulation.TButton', font=("Helvetica", 15))
        ttk.Style().configure('simulation.TCheckbutton', font=("Helvetica", 15))
        self.sidebar()
        self.settings = ttk.Frame(self.root)
        self.SingleTestCases = QuantumSingleTestCases()
        self.BulkTestCases = QuantumBulkTestCases(self.SingleTestCases)
        self.CompareTestCases = QuantumComparedTestCases()
        self.NoiseTestCases = QuantumNoiseTestCases()


    def clear(self):
        self.settings.destroy()
        if self.imageOptions != None:
            self.imageOptions.destroy()
            self.simulation.destroy()

    def SingleTestCasePage(self):
        self.clear()
        # Image setting
        self.settings = ttk.Frame(self.root)
        self.settings.grid(row=0, column=2, sticky="nwe")
        self.headline = ttk.Label(self.settings, text="Single Test Cases", width=50, font=("Helvetica", 26))
        self.headline.pack(pady=5, padx=5)
        self.ImageOptions(self.settings)
        self.SingleSimulation(self.settings)

    def NoiseTestCasePage(self):
        self.clear()
        # Image setting
        self.settings = ttk.Frame(self.root)
        self.settings.grid(row=0, column=2, sticky="nwe")
        self.headline = ttk.Label(self.settings, text="Noise Test Cases", width=50, font=("Helvetica", 26))
        self.headline.pack(pady=5, padx=5)
        self.ImageOptions(self.settings, noise=True)
        self.NoiseSimulation(self.settings)

    def BulkTestCasePage(self):
        self.clear()
        # Image setting
        self.settings = ttk.Frame(self.root)
        self.settings.grid(row=0, column=2, sticky="nwe")
        self.headline = ttk.Label(self.settings, text="Bulk Test Cases", width=50, font=("Helvetica", 26))
        self.headline.pack(pady=5, padx=5)
        self.ImageOptions(self.settings, cases=True)
        self.BulkSimulation(self.settings)

    def CompareTestCasePage(self):
        self.clear()
        # Image setting
        self.settings = ttk.Frame(self.root)
        self.settings.grid(row=0, column=2, sticky="nwe")
        self.headline = ttk.Label(self.settings, text="Compare Test Cases", width=50, font=("Helvetica", 26))
        self.headline.pack(pady=5, padx=5)
        self.ImageOptions(self.settings, cases=True)
        self.CompareSimulation(self.settings)

    def ImageOptions(self, frame, cases=False, noise=False):
        imageOptions = ttk.LabelFrame(frame, text="Image Options")
        ttk.Label(imageOptions, text="Width:", font=("Helvetica", 15)).pack(side=ttk.LEFT, padx=5, pady=5)
        self.width = ttk.Entry(imageOptions)
        self.width.pack(side=ttk.LEFT, padx=5, pady=5)
        self.width.insert(0, "2")
        ttk.Label(imageOptions, text="Height:", font=("Helvetica", 15)).pack(side=ttk.LEFT, padx=5, pady=5)
        self.height = ttk.Entry(imageOptions)
        self.height.pack(side=ttk.LEFT, padx=5, pady=5)
        self.height.insert(0, "2")
        ttk.Label(imageOptions, text="Color:", font=("Helvetica", 15)).pack(side=ttk.LEFT, padx=5, pady=5)
        self.color = ttk.Entry(imageOptions)
        self.color.pack(side=ttk.LEFT, padx=5, pady=5)
        self.color.insert(0, "2")
        if noise:
            ttk.Label(imageOptions, text="noise:", font=("Helvetica", 15)).pack(side=ttk.LEFT, padx=5, pady=5)
            self.noise = ttk.Entry(imageOptions)
            self.noise.insert(0, "0.0")
            self.noise.pack(side=ttk.LEFT, padx=5, pady=5)

        if cases:
            ttk.Label(imageOptions, text="request time:", font=("Helvetica", 15)).pack(side=ttk.LEFT, padx=5, pady=5)
            self.requestTime = ttk.Entry(imageOptions)
            self.requestTime.pack(side=ttk.LEFT, padx=5, pady=5)
            self.requestTime.insert(0, "0")

            ttk.Label(imageOptions, text="Cases:", font=("Helvetica", 15)).pack(side=ttk.LEFT, padx=5, pady=5)
            self.cases = ttk.Entry(imageOptions)
            self.cases.pack(side=ttk.LEFT, padx=5, pady=5)
            self.cases.insert(0, "100")

        self.saveCircuit = ttk.BooleanVar()
        ttk.Checkbutton(imageOptions, text="Save Circuit", style="simulation.TCheckbutton", variable=self.saveCircuit,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        imageOptions.pack(side=ttk.LEFT, pady=5, padx=5)
        self.imageOptions = imageOptions

    def BulkSimulation(self, frame):
        simulation = ttk.LabelFrame(self.root, text="Simulations")
        ttk.Button(simulation, text="Normal Sequential", width=10, style="simulation.TButton",
                   command=self.executeNormalSequentialImageBulk).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Normal Parallel", width=10, style="simulation.TButton",
                   command=self.executeNormalParallelImageBulk).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Task based", width=10, style="simulation.TButton").pack(side=ttk.LEFT, padx=5,
                                                                                             pady=5)
        ttk.Button(simulation, text="Vertical based", width=10, style="simulation.TButton",
                   command=self.executeVerticalParallelImageBulk).pack(side=ttk.LEFT, padx=5, pady=5)
        self.randomized = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Randomized", style="simulation.TCheckbutton", variable=self.randomized,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        self.logs = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Logs", style="simulation.TCheckbutton", variable=self.logs, offvalue=False,
                        onvalue=True).pack(side=ttk.LEFT, padx=5, pady=5)
        simulation.grid(row=0, column=2, sticky="w")
        self.simulation = simulation

    def CompareSimulation(self, frame):
        simulation = ttk.LabelFrame(self.root, text="Simulations")
        ttk.Button(simulation, text="Task Flow", width=10, style="simulation.TButton", command=self.executeCompareTask).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Circuit", width=10, style="simulation.TButton",
                   command=self.executeCompareCircuit).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Time Flow", width=10, style="simulation.TButton").pack(side=ttk.LEFT, padx=5,
                                                                                             pady=5)
        ttk.Button(simulation, text="Mixed Flow", width=10, style="simulation.TButton", command=self.executeCompareMixedFlow).pack(side=ttk.LEFT, padx=5, pady=5)
        self.randomized = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Randomized", style="simulation.TCheckbutton", variable=self.randomized,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        self.logs = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Logs", style="simulation.TCheckbutton", variable=self.logs, offvalue=False,
                        onvalue=True).pack(side=ttk.LEFT, padx=5, pady=5)
        simulation.grid(row=0, column=2, sticky="w")
        self.simulation = simulation

    def SingleSimulation(self, frame):
        simulation = ttk.LabelFrame(self.root, text="Simulations")
        ttk.Button(simulation, text="Normal Sequential", width=10, style="simulation.TButton",
                   command=self.executeNormalSequentialImage).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Normal Parallel", width=10, style="simulation.TButton",
                   command=self.executeNormalParallelImage).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Task based", width=10, style="simulation.TButton", command=self.executeTaskImage).pack(side=ttk.LEFT, padx=5,
                                                                                             pady=5)
        ttk.Button(simulation, text="Vertical based", width=10, style="simulation.TButton",
                   command=self.executeVerticalDistributionSingle).pack(side=ttk.LEFT, padx=5, pady=5)
        self.randomized = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Randomized", style="simulation.TCheckbutton", variable=self.randomized,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        self.logs = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Logs", style="simulation.TCheckbutton", variable=self.logs, offvalue=False,
                        onvalue=True).pack(side=ttk.LEFT, padx=5, pady=5)
        simulation.grid(row=0, column=2, sticky="w")
        self.simulation = simulation

    def NoiseSimulation(self, frame):
        simulation = ttk.LabelFrame(self.root, text="Simulations")
        ttk.Button(simulation, text="Normal", width=10, style="simulation.TButton",
                   command=self.executeNormalNoise).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Task", width=10, style="simulation.TButton",
                   command=self.executeTaskNoise).pack(side=ttk.LEFT, padx=5, pady=5)
        ttk.Button(simulation, text="Circuit Division", width=10, style="simulation.TButton",
                   command=self.executeCircuitNoise).pack(side=ttk.LEFT, padx=5, pady=5)
        self.bitflip = ttk.BooleanVar()
        ttk.Checkbutton(simulation,
                        text="Bit-flip", style="simulation.TCheckbutton", variable=self.bitflip,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        self.dephasing = ttk.BooleanVar()
        ttk.Checkbutton(simulation,
                        text="Dephasing", style="simulation.TCheckbutton", variable=self.dephasing,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        self.deporalization = ttk.BooleanVar()
        ttk.Checkbutton(simulation,
                        text="Deporalization", style="simulation.TCheckbutton", variable=self.deporalization,
                        onvalue=True, offvalue=False).pack(side=ttk.LEFT, padx=5, pady=5)
        self.logs = ttk.BooleanVar()
        ttk.Checkbutton(simulation, text="Logs", style="simulation.TCheckbutton", variable=self.logs, offvalue=False,
                        onvalue=True).pack(side=ttk.LEFT, padx=5, pady=5)
        simulation.grid(row=0, column=2, sticky="w")
        self.simulation = simulation

    def sidebar(self):
        sidebar = ttk.LabelFrame(self.root, text="Navigation")
        ttk.Button(sidebar, text="Single", width=15, style="sidebar.TButton", command=self.SingleTestCasePage).pack(
            pady=15)
        ttk.Button(sidebar, text="Noise", width=15, style="sidebar.TButton", command=self.NoiseTestCasePage).pack(
            pady=15)
        ttk.Button(sidebar, text="Bulk", width=15, style="sidebar.TButton", command=self.BulkTestCasePage).pack(pady=15)
        ttk.Button(sidebar, text="Compare", width=15, style="sidebar.TButton", command=self.CompareTestCasePage).pack(pady=15)
        sidebar.grid(row=0, column=0, sticky="nwe")


    def executeNormalNoise(self):
        print("Normal noise simulation!")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits ")
        print("Noise: ", float(self.noise.get()))
        if self.bitflip.get():
            print("------------------------ Bit-flip Noise --------------------------")
            self.NoiseTestCases.NormalImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), logs=self.logs.get(), model="bitflip", noise=float(self.noise.get()))

        if self.dephasing.get():
            print("------------------------ Dephasing Noise --------------------------")
            self.NoiseTestCases.NormalImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                            logs=self.logs.get(), model="dephase", noise=float(self.noise.get()))
        if self.deporalization.get():
            print("------------------------ Dephasing Noise --------------------------")
            self.NoiseTestCases.NormalImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                            logs=self.logs.get(), model="depolarize", noise=float(self.noise.get()))

    def executeTaskNoise(self):
        print("Task noise simulation!")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits")
        print("Noise: ", float(self.noise.get()))
        if self.bitflip.get():
            print("------------------------ Bit-flip Noise --------------------------")
            self.NoiseTestCases.TaskImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), logs=self.logs.get(), model="bitflip", noise=float(self.noise.get()))

        if self.dephasing.get():
            print("------------------------ Dephasing Noise --------------------------")
            self.NoiseTestCases.TaskImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                          logs=self.logs.get(), model="dephase", noise=float(self.noise.get()))

        if self.deporalization.get():
            print("------------------------ Deporalization Noise --------------------------")
            self.NoiseTestCases.TaskImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                          logs=self.logs.get(), model="depolarize", noise=float(self.noise.get()))

    def executeCircuitNoise(self):
        print("Circuit noise simulation!")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits")
        print("Noise: ", float(self.noise.get()))
        if self.bitflip.get():
            print("------------------------ Bit-flip Noise --------------------------")
            self.NoiseTestCases.CircuitImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), logs=self.logs.get(),
                                                   model="bitflip", noise=float(self.noise.get()))
        if self.dephasing.get():
            print("------------------------ Dephase Noise --------------------------")
            self.NoiseTestCases.CircuitImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), logs=self.logs.get(),
                                                   model="dephase", noise=float(self.noise.get()))

        if self.deporalization.get():
            print("------------------------ Depolarization Noise --------------------------")
            self.NoiseTestCases.CircuitImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), logs=self.logs.get(),
                                                   model="depolarize", noise=float(self.noise.get()))

    def executeVerticalDistributionSingle(self):
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.SingleTestCases.CircuitDistribution(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                                   rand=self.randomized.get(), logs=self.logs.get(),
                                                   saveCircuit=self.saveCircuit.get())

        print("Total execution time: ", totalTime["time"], " with total gate cost: ", totalTime["gates"])

    def executeNormalSequentialImage(self):
        print("Normal Sequential Image")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.SingleTestCases.NormalImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                         rand=self.randomized.get(), logs=self.logs.get(),
                                         saveCircuit=self.saveCircuit.get())

        print("Total execution time: ", totalTime["time"], " with total gate cost: ", totalTime["gates"])

    def executeTaskImage(self):
        print("Task Image Distribution")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.SingleTestCases.TaskImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                         rand=self.randomized.get(), logs=self.logs.get(),
                                         saveCircuit=self.saveCircuit.get())

        print("Total execution time: ", totalTime["time"], " with total gate cost: ", totalTime["gates"])

    def executeNormalParallelImage(self):
        print("Normal Parallel Image")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.SingleTestCases.NormalImage(int(self.width.get()), int(self.height.get()), int(self.color.get()),
                                         rand=self.randomized.get(), logs=self.logs.get(),
                                         saveCircuit=self.saveCircuit.get(), parallel=True)

        print("Total execution time: ", totalTime["time"], " with total gate cost: ", totalTime["gates"])

    def executeNormalSequentialImageBulk(self):
        print("Normal Sequential Bulk Image")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.BulkTestCases.NormalBulkImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), int(self.cases.get()),
                                           rand=self.randomized.get(), logs=self.logs.get(),
                                           saveCircuit=self.saveCircuit.get())

        print("Total execution time: ", totalTime, " cases: ", int(self.cases.get()))

    def executeNormalParallelImageBulk(self):
        start = time.time()
        print("Normal Parallel Bulk Image")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.BulkTestCases.NormalBulkImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), int(self.cases.get()),
                                           rand=self.randomized.get(), logs=self.logs.get(),
                                           saveCircuit=self.saveCircuit.get(), parallel=True)

        print("Total execution time: ", totalTime, " cases: ", int(self.cases.get()))
        end = time.time()
        #print(end - start)

    def executeVerticalParallelImageBulk(self):
        print("Vertical Parallel Bulk Image")
        print(self.width.get(), "x", self.height.get(), " with ", self.color.get(), " color Qubits and random: ",
              self.randomized.get())
        totalTime = self.BulkTestCases.VerticalBulkImage(int(self.width.get()), int(self.height.get()), int(self.color.get()), int(self.cases.get()),
                                           rand=self.randomized.get(), logs=self.logs.get(),
                                           saveCircuit=self.saveCircuit.get())

        print("Total execution time: ", totalTime, " cases: ", int(self.cases.get()))

    def executeCompareCircuit(self):
        start = time.time()
        width = int(self.width.get())
        height = int(self.height.get())
        color = int(self.color.get())
        cases = int(self.cases.get())
        rand = self.randomized.get()
        logs = self.logs.get()

        print()
        print('------------------ Calculating Average Circuit Distribution ',
              ': --------------------------')
        yQubit = math.ceil(math.log(height, 2))
        xQubit = math.ceil(math.log(width, 2))
        print(width, "x", self.height.get(), " with ", self.color.get(), " color Qubits, total Qubits for Image:", (xQubit+yQubit+color)," and is random: ",
              self.randomized.get())
        #Execute as another thread for performance
        thread = Thread(target=self.CompareTestCases.CompareCircuitDistribution, args=(width, height, color, cases, rand, [], logs, False))
        thread.start()
        thread.join()
        #self.CompareTestCases.CompareCircuitDistribution(int(self.width.get()), int(self.height.get()), int(self.color.get()), int(self.cases.get()),
        #                                   rand=self.randomized.get(), logs=self.logs.get(),
        #                                   saveCircuit=self.saveCircuit.get())
        end = time.time()
        print("Simulation finished in : ", (end - start), " seconds")


    def executeCompareMixedFlow(self):
        start = time.time()
        cases = int(self.cases.get())
        rand = self.randomized.get()
        logs = self.logs.get()
        print()
        print('------------------ Calculating Total Average time Difference with Task Distribution in Mixed Flow ',
              ': --------------------------')
        #Execute as another thread for performance
        thread = Thread(target=self.CompareTestCases.CompareMixedFlow, args=(cases, rand, logs))
        thread.start()
        thread.join()
        end = time.time()
        print("Simulation finished in : ", (end - start), " seconds")

    def executeCompareTask(self):
        start = time.time()
        width = int(self.width.get())
        height = int(self.height.get())
        color = int(self.color.get())
        cases = int(self.cases.get())
        rand = self.randomized.get()
        logs = self.logs.get()
        requestTime = int(self.requestTime.get())
        print()
        print('------------------ Calculating Total Average & Total time Difference with Task Distribution ',
              ': --------------------------')
        yQubit = math.ceil(math.log(height, 2))
        xQubit = math.ceil(math.log(width, 2))
        print(width, "x", self.height.get(), " with ", self.color.get(), " color Qubits, total Qubits for Image:", (xQubit+yQubit+color)," and is random: ",
              self.randomized.get())
        distribution = []
        if requestTime > 0:
            distribution = random.exponential(size=cases, scale=requestTime)
            snsfigure = sns.displot(data=distribution)
            snsfigure.savefig("images/Task/distribution_rt.png")
        #Execute as another thread for performance
        for i in range(10):
            print("RUN", i)
            thread = Thread(target=self.CompareTestCases.CompareTaskDistribution, args=(width, height, color, cases, rand, distribution, logs))
            thread.start()
            thread.join()
        end = time.time()
        print("Simulation finished in : ", (end - start), " seconds")