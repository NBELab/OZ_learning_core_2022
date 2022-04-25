import os

from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.Configurators.PulseSynapseConfigurator import PulseSynapseConfigurator
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from NeuralEmulator.OZNeuron import OZNeuron
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Preprocessing.PosPreprocessingBlock import PosPreprocessingBlock
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlock
from NeuralEmulator.PulseSynapse import PulseSynapse
from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource
import random


class NeuronsGenerator:
    def __init__(self, neuronsNumber, synapse, lowerBound=100.0 * (10 ** -3), upperBound=800.0 * (10 ** -3), randomVals=False):

        noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
        ozNeuronConfigurator = OZNeuronConfigurator()

        neurons = []
        leaks = []

        if randomVals is False:
            start = upperBound
            delta = (upperBound - lowerBound) / neuronsNumber
            for x in range(neuronsNumber):
                normalLeakSource = NormalLeakSource(SimpleVoltageSource(start), noramalLeakSourceConfigurator)
                ozNeuron = OZNeuron(synapse, normalLeakSource, ozNeuronConfigurator)
                leaks.append(normalLeakSource)
                neurons.append(ozNeuron)
                start -= delta
        else:
            lowerBound = int(lowerBound * (10 ** 3))
            uppderBound = int(upperBound * (10 ** 3))
            vals = set()

            while len(vals) != neuronsNumber:
                vlk = random.randint(lowerBound, uppderBound)
                vals.add(vlk)

            for x in range(neuronsNumber):
                vlk = vals.pop()
                vlk = vlk * (10 ** -3)
                normalLeakSource = NormalLeakSource(SimpleVoltageSource(vlk), noramalLeakSourceConfigurator)
                ozNeuron = OZNeuron(synapse, normalLeakSource, ozNeuronConfigurator)
                leaks.append(normalLeakSource)
                neurons.append(ozNeuron)

        self.neurons = neurons
        self.leaks = leaks

    def getNeurons(self):
        return self.neurons

    def getLeaks(self):
        return self.leaks


if __name__ == "__main__":
    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    vin = SimpleVoltageSource()
    preProcessBlock = PreprocessingBlock(vin)
    vposPort = PosPreprocessingBlock(preProcessBlock)

    g = NeuronsGenerator(50, vposPort, randomVals=True)
    neurons = g.getNeurons()
    print("sf")
