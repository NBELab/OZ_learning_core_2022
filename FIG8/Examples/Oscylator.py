import os
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd
from numpy import single

from NeuralEmulator.Adder import Adder
from NeuralEmulator.ClusterSources import ClusterCurrentSource, ClusterVoltageSource
from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.Configurators.PulseSynapseConfigurator import PulseSynapseConfigurator
from NeuralEmulator.Configurators.TemporalConfigurator import TemporalConfigurator
from NeuralEmulator.ErrorBlock import ErrorBlock
from NeuralEmulator.LearningBlock import LearningBlock
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from NeuralEmulator.OZNeuron import OZNeuron
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Preprocessing.PosPreprocessingBlock import PosPreprocessingBlock
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlock
from NeuralEmulator.PulseSynapse import PulseSynapse
from NeuralEmulator.TemporalIntegration import TemporalIntegration
from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource
from NeuralEmulator.Utils.Generators import Generator
from NeuralEmulator.Utils.Utils import playSound
from NeuralEmulator.VoltageSources.LinearSignal import LinearSignal, OscylatorRefSignal, PulseSource
from NeuralEmulator.VoltageSources.SinSignal import SinSignal, SquaredSin

OUTOUT_FILE = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\Learning\lr.csv"

os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

SIM_TIME = 3.0
NUMBER_OF_NEURONS = 8
LR = 50 * (10 ** -3)
osyFactor = 1 / (2)

generator = Generator()

pulseSynapseConfigurator = PulseSynapseConfigurator()
noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
ozNeuronConfigurator = OZNeuronConfigurator()
temporalConfigurator = TemporalConfigurator()

# Adders
adderForX1 = Adder()
adderForX2 = Adder()

# Pulse
pulseSource = PulseSource(50 * (10 ** -3), 30 * (10 ** -3), 800 * (10 ** -3))
clusterVoltageSourceX11 = ClusterVoltageSource([adderForX1, pulseSource])

L1 = [adderForX1, adderForX2, pulseSource, clusterVoltageSourceX11]

# x1 Preprocess
preProcessBlockx1 = PreprocessingBlock(clusterVoltageSourceX11)
vposPortx1 = PosPreprocessingBlock(preProcessBlockx1)
vnegPortx1 = NegPreprocessingBlock(preProcessBlockx1)

# x2 Preprocess
preProcessBlockx2 = PreprocessingBlock(adderForX2)
vposPortx2 = PosPreprocessingBlock(preProcessBlockx2)
vnegPortx2 = NegPreprocessingBlock(preProcessBlockx2)

L2 = [preProcessBlockx1, vposPortx1, vnegPortx1, preProcessBlockx2, vposPortx2, vnegPortx2]

# Synapses
positivePulseSynapsex1 = PulseSynapse(vposPortx1, pulseSynapseConfigurator)
negativePulseSynapsex1 = PulseSynapse(vnegPortx1, pulseSynapseConfigurator)

positivePulseSynapsex2 = PulseSynapse(vposPortx2, pulseSynapseConfigurator)
negativePulseSynapsex2 = PulseSynapse(vnegPortx2, pulseSynapseConfigurator)

L3 = [positivePulseSynapsex1, negativePulseSynapsex1, positivePulseSynapsex2, negativePulseSynapsex2]

# Clustered Sources
clusteredPosCurrentSrc = ClusterCurrentSource([positivePulseSynapsex1, positivePulseSynapsex2])
clusteredNEGCurrentSrc = ClusterCurrentSource([negativePulseSynapsex1, negativePulseSynapsex2])

L4 = [clusteredPosCurrentSrc, clusteredNEGCurrentSrc]

# Leak
#L5 = generator.generateNormalLeakSources(int(NUMBER_OF_NEURONS / 2), 700.0 * (10 ** -3), 15.0 * (10 ** -3))
L5 = generator.generateUniformLeaks()
# Neurons
posNeurons = generator.generateEnsemble(clusteredPosCurrentSrc, L5)
negNeurons = generator.generateEnsemble(clusteredNEGCurrentSrc, L5)
L6 = posNeurons + negNeurons

# Temporal Integration
posTemporals = generator.generateTempIntegrations(40 * (10 ** -3), posNeurons)
negTemporals = generator.generateTempIntegrations(40 * (10 ** -3), negNeurons)
L7 = posTemporals + negTemporals

# Oscylator function
x1ref = OscylatorRefSignal(clusterVoltageSourceX11, adderForX2, osyFactor)
x2ref = OscylatorRefSignal(adderForX2, adderForX1, -osyFactor)
L8 = [x1ref, x2ref]

# ErrorCKT
errorBlockX1 = ErrorBlock(adderForX1, x1ref, NUMBER_OF_NEURONS)
errorBlockx2 = ErrorBlock(adderForX2, x2ref, NUMBER_OF_NEURONS)

L9 = [errorBlockX1, errorBlockx2]
# LearningBlocks

x1LearningBlocks = generator.generateLearningBlock(LR, L7, errorBlockX1)
x2LearningBlocks = generator.generateLearningBlock(LR, L7, errorBlockx2)

L10 = x1LearningBlocks + x2LearningBlocks

adderForX1.setListOfSources(x1LearningBlocks)
adderForX2.setListOfSources(x2LearningBlocks)

layers = [L1, L2, L3, L4, L5, L6, L7, L8, L9, L10]

timeAxis = []
sinAdderVals = []
linAdderVals = []

simResTime = ozNeuronConfigurator.getSimTimeTick()
SIMULATION_TICKS = int(SIM_TIME // simResTime)

timeAxisVal = 0
startTime = time.time()

x1LearninBlocksOutput = [[] for x in x1LearningBlocks]

neuronsOutput = [[] for x in L6]
neuronsTemporalOutput = [[] for x in L7]

pulseProbe = []
x11Probe = []
x2Probe = []

for tick in range(SIMULATION_TICKS):
    print("\rSTEP {}/{}".format(tick + 1, SIMULATION_TICKS))
    timeAxis.append(timeAxisVal)
    timeAxisVal += simResTime

    for layer in layers:
        for obj in layer:
            obj.run()

    # for n in range(len(x1LearningBlocks)):
    #     x1LearninBlocksOutput[n].append(x1LearningBlocks[n].getVoltage())
    for n in range(len(L6)):
        neuronsOutput[n].append(L6[n].getVoltage())

    for n in range(len(L7)):
        neuronsTemporalOutput[n].append(L7[n].getVoltage())

    pulseProbe.append(pulseSource.getVoltage())
    x11Probe.append(adderForX1.getVoltage())
    x2Probe.append(adderForX2.getVoltage())

print("\nsimulation runtime {}s".format(time.time() - startTime))

# playSound()

# fig, axs = plt.subplots(8, 3)
#
# axs[0, 0].plot(timeAxis, pulseProbe)
# axs[1, 0].plot(timeAxis, x11Probe)
# axs[2, 0].plot(timeAxis, x2Probe)
# axs[3, 0].plot(x11Probe, x2Probe)
#
# for n in range(len(L6)):
#     axs[n, 1].plot(timeAxis, neuronsOutput[n])
#
# for n in range(len(L7)):
#     axs[n, 2].plot(timeAxis, neuronsTemporalOutput[n])
#
# df = pd.DataFrame({'time': timeAxis,
#                    'X1': x11Probe,
#                    'X2': x2Probe})
#
# fPath = r'C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\Oscylator\oscylator.csv'
# df.to_csv(fPath, index=False)

plt.plot(x11Probe, x2Probe)
plt.show()
