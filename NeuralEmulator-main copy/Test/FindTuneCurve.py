import matplotlib.pyplot as plt
import pandas as pd

from NeuralEmulator.Configurators.PulseSynapseVWConfigurator import PulseSynapseVWConfigurator
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlock
from NeuralEmulator.Preprocessing.PosPreprocessingBlock import PosPreprocessingBlock
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Configurators.PulseSynapseConfigurator import PulseSynapseConfigurator
from NeuralEmulator.PulseSynapse import PulseSynapse, PulseSynapseWeighted
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.OZNeuron import OZNeuron
from NeuralEmulator.Test.SimpleLeakCurrent import SimpleLeakCurrent
from NeuralEmulator.Utils.Generators import Generator
from NeuralEmulator.Utils.NeuronsGenerator import NeuronsGenerator
from NeuralEmulator.Utils.Utils import getFreqForSpikesVec
from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource
from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from numba import jit
from concurrent.futures.thread import ThreadPoolExecutor

from NeuralEmulator.VoltageSources.LinearSignal import StaticSource

OUTOUT_FOLDER = r'C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\results'
OUTOUT_FILE = OUTOUT_FOLDER + "\\bounded_bounded.csv"


def runSimObj(obj):
    obj.run()


def buildNeuron(vinSource, vinConfigurator, vlkVal, noramalLeakSourceConfigurator, ozNeuronConfigurator):
    pulseSynapse = PulseSynapse(vinSource, vinConfigurator)

    vlk = SimpleVoltageSource(vlkVal)
    normalLeakSource = NormalLeakSource(vlk, noramalLeakSourceConfigurator)

    ozNeuron = OZNeuron(pulseSynapse, normalLeakSource, ozNeuronConfigurator)
    return ozNeuron


if __name__ == "__main__":
    import os
    import time
    import sys

    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    pulseSynapseConfigurator = PulseSynapseConfigurator()
    noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
    ozNeuronConfigurator = OZNeuronConfigurator()
    pulseSynapseVWConfigurator = PulseSynapseVWConfigurator()

    # vin
    vin = SimpleVoltageSource()
    preProcessBlock = PreprocessingBlock(vin)
    vposPort = PosPreprocessingBlock(preProcessBlock)
    vnegPort = NegPreprocessingBlock(preProcessBlock)

    # Synapses
    staticSource = StaticSource(2.4)
    positivePulseSynapse = PulseSynapseWeighted(vposPort, staticSource, pulseSynapseVWConfigurator)
    negativePulseSynapse = PulseSynapseWeighted(vnegPort, staticSource, pulseSynapseVWConfigurator)

    # normalLeakSource = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource(745.0 * (10 ** -3)))
    # normalLeakSource2 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource(700.0 * (10 ** -3)))
    # normalLeakSource3 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource(600.0 * (10 ** -3)))
    # normalLeakSource4 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource(450.0 * (10 ** -3)))
    #
    # normalLeakSource5 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource((745.0) * (10 ** -3)))
    # normalLeakSource6 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource((700.0) * (10 ** -3)))
    # normalLeakSource7 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource((600.0) * (10 ** -3)))
    # normalLeakSource8 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource((450.0) * (10 ** -3)))
    #
    # # Neuron
    # ozNeuron = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource)
    # ozNeuron2 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource2)
    # ozNeuron3 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource3)
    # ozNeuron4 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource4)
    #
    # ozNeuron5 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource5)
    # ozNeuron6 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource6)
    # ozNeuron7 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource7)
    # ozNeuron8 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource8)
    #   Bounded L55 = Generator().generateNormalLeakSources(int(NUMBER_OF_NEURONS / 2), 730.0 * (10 ** -3), 15.0 * (10 ** -3))

    NUMBER_OF_NEURONS = 8
    L55 = Generator().generateNormalLeakSources(int(NUMBER_OF_NEURONS / 2), 500.0 * (10 ** -3), 80.0 * (10 ** -3))
    L55 = Generator().generateNormalLeakSources(int(NUMBER_OF_NEURONS / 2), 730.0 * (10 ** -3), 15.0 * (10 ** -3))  # Bounded

    posNeurons = Generator().generateEnsemble(positivePulseSynapse, L55)
    negNeurons = Generator().generateEnsemble(negativePulseSynapse, L55)
    L3 = posNeurons + negNeurons

    # Layers
    L1 = [vin, preProcessBlock]
    L2 = [negativePulseSynapse, positivePulseSynapse]

    #  L3 = [ozNeuron, ozNeuron2, ozNeuron3, ozNeuron4,ozNeuron5,ozNeuron6,ozNeuron7,ozNeuron8]

    layers = [L1, L2, L3]

    neuronsVout = {}
    neuronsFreqs = {"VIN": []}
    keyToObj = {}
    for x in range(len(L3)):
        k = "n{}".format(x)
        neuronsVout[k] = []
        neuronsFreqs[k] = []
        keyToObj[k] = L3[x]

    SIM_TIME = 1.0
    simResTime = ozNeuronConfigurator.getSimTimeTick()
    numberOfTicksPerOneSec = int(SIM_TIME // simResTime)

    VIN = -1
    STEP_SIZE = 50 * (10 ** -3)
    VIN_MAX = 1

    VIN = VIN - STEP_SIZE

    totalIncrements = int((VIN_MAX - VIN) // STEP_SIZE) + 1
    currentStep = 1

    start = time.time()


    while VIN != 1:
        VIN += STEP_SIZE
        if VIN > VIN_MAX:
            VIN = VIN_MAX

        print("STEP {}/{} VIN {}".format(currentStep, totalIncrements, VIN))
        neuronsFreqs["VIN"].append(VIN)

        vin.setVoltage(VIN)
        steps = []

        for t in range(numberOfTicksPerOneSec):
            steps.append(t)
            for l in layers:
                for obj in l:
                    obj.run()

            for ko in keyToObj.keys():
                neuronsVout[ko].append(keyToObj[ko].getVoltage())

        for k in neuronsFreqs.keys():
            if k != "VIN":
                f1 = getFreqForSpikesVec(neuronsVout[k])
                # if k == "n6":
                #     print("-I- freq {}".format(f1))
                #     plt.plot(steps, neuronsVout[k])
                #     plt.show()

                s = neuronsFreqs[k]
                s.append(f1)
                neuronsFreqs[k] = s
                neuronsVout[k] = []

        currentStep += 1


    print("\nTime {:.3f}s".format(time.time() - start))
    df = pd.DataFrame(neuronsFreqs)
    df.to_csv(OUTOUT_FILE, header=True, index=False)
    plt.plot()

df = pd.read_csv(OUTOUT_FILE)
x = df["VIN"]
for col in df.columns:
    if col != "VIN":
        plt.plot(x, df[col])

plt.grid()
plt.axhline(y=0, color='k')
plt.axvline(x=0, color='k')

plt.show()
