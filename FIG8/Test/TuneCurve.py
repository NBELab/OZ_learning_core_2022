import matplotlib.pyplot as plt
import pandas as pd
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlock
from NeuralEmulator.Preprocessing.PosPreprocessingBlock import PosPreprocessingBlock
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Configurators.PulseSynapseConfigurator import PulseSynapseConfigurator
from NeuralEmulator.PulseSynapse import PulseSynapse
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.OZNeuron import OZNeuron
from NeuralEmulator.Test.SimpleLeakCurrent import SimpleLeakCurrent
from NeuralEmulator.Utils.NeuronsGenerator import NeuronsGenerator
from NeuralEmulator.Utils.Utils import getFreqForSpikesVec
from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource
from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from numba import jit
from concurrent.futures.thread import ThreadPoolExecutor

OUTOUT_FOLDER = r'C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\tuneCurves'
OUTOUT_FILE = OUTOUT_FOLDER + "\\curves.csv"


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

    # vin
    vin = SimpleVoltageSource()
    preProcessBlock = PreprocessingBlock(vin)
    vposPort = PosPreprocessingBlock(preProcessBlock)
    vnegPort = NegPreprocessingBlock(preProcessBlock)

    # Synapses
    positivePulseSynapse = PulseSynapse(vposPort, pulseSynapseConfigurator)
    negativePulseSynapse = PulseSynapse(vnegPort, pulseSynapseConfigurator)

    NEURON_NUM = 8

    negNeurons = NeuronsGenerator(NEURON_NUM // 2, negativePulseSynapse, randomVals=False)
    posNeurons = NeuronsGenerator(NEURON_NUM // 2, positivePulseSynapse, randomVals=False)

    # Layers
    L1 = [vin, preProcessBlock]
    L2 = [negativePulseSynapse, positivePulseSynapse]
    L3 = negNeurons.getNeurons() + posNeurons.getNeurons()

    layers = [L1, L2, L3]

    neuronsVout = {}
    neuronsFreqs = {"VIN": []}
    keyToObj = {}
    for x in range(NEURON_NUM):
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

        sys.stdout.write("\rSTEP {}/{}".format(currentStep, totalIncrements))
        sys.stdout.flush()
        currentStep += 1
        VIN += STEP_SIZE
        if VIN > VIN_MAX:
            VIN = VIN_MAX

        neuronsFreqs["VIN"].append(VIN)

        vin.setVoltage(VIN)

        for t in range(numberOfTicksPerOneSec):
            for l in layers:
                for obj in l:
                    obj.run()

            for ko in keyToObj.keys():
                neuronsVout[ko].append(keyToObj[ko].getVoutVal())

        for k in neuronsFreqs.keys():
            if k != "VIN":
                f1 = getFreqForSpikesVec(neuronsVout[k])
                s = neuronsFreqs[k]
                s.append(f1)
                neuronsFreqs[k] = s
                neuronsVout[k] = []

    print("\nTime {:.3f}s".format(time.time() - start))
    df = pd.DataFrame(neuronsFreqs)
    df.to_csv(OUTOUT_FILE, header=True, index=False)
    plt.plot()

df = pd.read_csv(r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\tuneCurves\curves.csv")
x = df["VIN"]
for col in df.columns:
    if col != "VIN":
        plt.plot(x, df[col])

plt.show()
