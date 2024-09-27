from qiskit import *
from qiskit_aer import Aer, AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error, depolarizing_error
from qiskit.quantum_info import Statevector


class QuantumMeasurement:
    qUtil = None
    circuit = None
    qCircuit = None
    qImage = None
    qKeyImage = None
    classicalRegister = []

    def __init__(self, qCircuit, qUtil, circuit, qImage, qKeyImage, classicalRegister):
        self.qCircuit = qCircuit
        self.qUtil = qUtil
        self.circuit = circuit
        self.qImage = qImage
        self.qKeyImage = qKeyImage
        self.classicalRegister = classicalRegister

    def noise_model(self, p=0.5, model="bitflip"):
        noisemodel = None
        if model == "bitflip":
            # QuantumError objects
            error_x = pauli_error([('X', p), ('I', 1 - p)])
            error_cx = error_x.tensor(error_x)

            # Add errors to noise model
            noise_bit_flip = NoiseModel()
            #noise_bit_flip.add_all_qubit_quantum_error(error_x, "measure")
            noise_bit_flip.add_all_qubit_quantum_error(error_x, "x")
            noise_bit_flip.add_all_qubit_quantum_error(error_cx, ["cx"])
            noisemodel = noise_bit_flip
        elif model == "dephase":
            phase_flip = pauli_error([('Z', p), ('I', 1 - p)])
            error_cz = phase_flip.tensor(phase_flip)

            # Add errors to noise model
            phase = NoiseModel()
            #phase.add_all_qubit_quantum_error(phase_flip, "measure")
            phase.add_all_qubit_quantum_error(phase_flip, "z")
            phase.add_all_qubit_quantum_error(error_cz, ["cz"])
            noisemodel = phase
        elif model == "depolarize":
            error = depolarizing_error(p, 1)
            depolarize = NoiseModel()
            depolarize.add_all_qubit_quantum_error(error, ['u1', 'u2', 'u3'])
            noisemodel = depolarize

        return noisemodel

    def getNoise(self, currentCircuit, desiredCircuit, allQubits=False, noise=0.5, model="bitflip", remove=True, mode="normal"):
        self.measureCircuit(currentCircuit, currentCircuit.qImage, allQubits=allQubits, remove=remove, mode=mode)
        self.measureCircuit(desiredCircuit, desiredCircuit.qImage, allQubits=allQubits, remove=remove, mode="normal")
        nm = self.noise_model(noise, model=model)
        sim_noise = AerSimulator(noise_model=nm)
        sim = AerSimulator()
        # Transpile circuit for noisy basis gates
        circ_tnoise = transpile(currentCircuit.circuit, sim_noise)
        circ_t = transpile(desiredCircuit.circuit)
        perfect = sim.run(circ_t, shots=8024).result()
        # Run and get counts
        noise = sim_noise.run(circ_tnoise, shots=8024).result()
        # print(noise)
        dm1 = perfect.get_counts()
        dm2 = noise.get_counts()
        dm1_count = 0
        dm2_count = 0
        print(dm1)
        #print("DM: ---------")
        #print(dm2)

        # remove duplicates
        dm1 = self.qUtil.remove_duplicates_in_dict(dm1)
        dm2 = self.qUtil.remove_duplicates_in_dict(dm2)
        desiredCircuit.qImage.states = dm2
        keystates = self.qUtil.checkEncryption(desiredCircuit.qImage, desiredCircuit.qKeyImage, mode=mode)
        print("result state: ", keystates["result"])
        for key in keystates["result"]:
            if key in dm1:
                dm1_count = dm1_count + dm1[key]
            if key in dm2:
                dm2_count = dm2_count + dm2[key]
        print('COUNTS: ')
        print("DM1 Count: ", dm1_count)
        print("DM1 len: ", len(dm1))
        print("DM2 Count: ", dm2_count)
        print("DM2 len: ", len(dm2))
        #result = (dm2_count - (dm1_count / len(dm2))) / (dm1_count / 100)
        result = ((dm2_count) / (dm1_count)) * 100
        print("Fidelity 1: ", result)

    def getStates(self, qCircuit, image, allQubits=False, remove=True, shots=8024, mode="normal"):
        # print("---------SHOTS: ", shots, "----------")
        self.measureCircuit(qCircuit, image, allQubits=allQubits, remove=remove, mode=mode)
        simulator = AerSimulator()
        tc = transpile(qCircuit.circuit)
        result = simulator.run(tc, shots=shots).result()
        counts = result.get_counts(tc)

        if allQubits:
            image.states = counts.keys()
        else:
            image.ogstates = counts.keys()
            image.states = []
            for key in counts.keys():
                key = key.replace(" ", "")
                image.states.append(key[-image.nQubit:])
        if remove:
            self.removeMeasureCircuit(qCircuit, image, allQubits)
        return image.states

    def removeMeasureCircuit(self, qCircuit, image, allQubits=False):
        number = 2 + image.nQubit + image.colorQubit
        if allQubits:
            number = number * 2
        lenG = len(qCircuit.circuit.data) - 1
        for i in range(number):
            qCircuit.circuit.data.pop(lenG - i)

    def addMeasureBeforeMeasurement(self, qcircuit, qImage, n, remove=True):
        for ch in qImage.colorQubits:
            qcircuit.circuit.h(ch)
        for c1 in range(qImage.colorQubit):
            qcircuit.circuit.measure(qImage.colorQubits[c1], n)
            n = n + 1

        for c2 in range(qImage.positionQubit):
            qcircuit.circuit.measure(qImage.positionQubits[c2], n)
            n = n + 1
        return n

    def measureCircuit(self, qcircuit, qImage, allQubits=False, remove=True, mode="normal"):
        qcircuit.circuit.barrier()
        qcircuit.circuit.barrier()
        if mode == "circuit" and allQubits:
            n = 0
            n = self.addMeasureBeforeMeasurement(qcircuit, qcircuit.qImage, n, remove=remove)
            n = self.addMeasureBeforeMeasurement(qcircuit, qcircuit.qKeyImage, n)
            for c1 in range(qcircuit.qImage.nQubit, qcircuit.qImage.nQubit + 3):
                self.circuit.measure(c1, n)
                n = n + 1
            return ""

        # Add the measurements, first add for all colorQubits
        n = 0
        n = self.addMeasureBeforeMeasurement(qcircuit, qImage, n, remove=remove)
        if allQubits:
            if qImage.name == 'Normal Image':
                # for kq in self.qKeyImage.colorQubits:
                #    self.circuit.h(kq)
                self.addMeasureBeforeMeasurement(qcircuit, qcircuit.qKeyImage, n)
            elif qImage.name == "Teleported QImage":
                # self.addMeasureBeforeMeasurement(self.qImage, n)
                n = self.addMeasureBeforeMeasurement(qcircuit, qcircuit.qKeyImage, n)
                #for c1 in range(qcircuit.qKeyImage.nQubit + qcircuit.qKeyImage.nQubit, qcircuit.qKeyImage.nQubit + qcircuit.qKeyImage.nQubit + qcircuit.qKeyImage.nQubit):
                #    self.circuit.measure(c1, n)
                #    n = n + 1
            else:
                # for Iq in self.qImage.colorQubits:
                #    self.circuit.h(Iq)
                self.addMeasureBeforeMeasurement(qcircuit, qcircuit.qImage, n)

        self.circuit.barrier()
