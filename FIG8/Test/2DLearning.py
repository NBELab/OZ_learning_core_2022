import os
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd
from numpy import single

from NeuralEmulator.Adder import Adder
from NeuralEmulator.ClusterSources import ClusterCurrentSource
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
from NeuralEmulator.VoltageSources.LinearSignal import LinearSignal
from NeuralEmulator.VoltageSources.SinSignal import SinSignal, SquaredSin

OUTOUT_FILE = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\Learning\lr.csv"

os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

SIM_TIME = 1.0

pulseSynapseConfigurator = PulseSynapseConfigurator()
noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
ozNeuronConfigurator = OZNeuronConfigurator()
temporalConfigurator = TemporalConfigurator()

# VIN
vinSin = SinSignal(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 2)
vinLin = LinearSignal(1.0, ozNeuronConfigurator.getSimTimeTick())

# vref = SquaredSin(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 2)


# Sin Preprocess
preProcessBlockSin = PreprocessingBlock(vinSin)
vposPortSin = PosPreprocessingBlock(preProcessBlockSin)
vnegPortSin = NegPreprocessingBlock(preProcessBlockSin)

# Linear Preprocess
preProcessBlockLin = PreprocessingBlock(vinLin)
vposPortLin = PosPreprocessingBlock(preProcessBlockSin)
vnegPortLin = NegPreprocessingBlock(preProcessBlockSin)

# Synapses
positivePulseSynapseSin = PulseSynapse(vposPortSin, pulseSynapseConfigurator)
negativePulseSynapseSin = PulseSynapse(vnegPortSin, pulseSynapseConfigurator)

positivePulseSynapseLin = PulseSynapse(vposPortLin, pulseSynapseConfigurator)
negativePulseSynapseLin = PulseSynapse(vnegPortLin, pulseSynapseConfigurator)

# Clustered Sources
clusteredPosCurrentSrc = ClusterCurrentSource([positivePulseSynapseSin, positivePulseSynapseLin])
clusteredNEGCurrentSrc = ClusterCurrentSource([negativePulseSynapseSin, negativePulseSynapseLin])

# Leak
normalLeakSource1 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(784.0 * (10 ** -3)))
normalLeakSource2 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(770.0 * (10 ** -3)))
normalLeakSource3 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(755.0 * (10 ** -3)))
normalLeakSource4 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(735.0 * (10 ** -3)))

# Neuron
ozNeuron1 = OZNeuron(ozNeuronConfigurator, clusteredPosCurrentSrc, normalLeakSource1)
ozNeuron2 = OZNeuron(ozNeuronConfigurator, clusteredPosCurrentSrc, normalLeakSource2)
ozNeuron3 = OZNeuron(ozNeuronConfigurator, clusteredPosCurrentSrc, normalLeakSource3)
ozNeuron4 = OZNeuron(ozNeuronConfigurator, clusteredPosCurrentSrc, normalLeakSource4)

ozNeuron5 = OZNeuron(ozNeuronConfigurator, clusteredNEGCurrentSrc, normalLeakSource1)
ozNeuron6 = OZNeuron(ozNeuronConfigurator, clusteredNEGCurrentSrc, normalLeakSource2)
ozNeuron7 = OZNeuron(ozNeuronConfigurator, clusteredNEGCurrentSrc, normalLeakSource3)
ozNeuron8 = OZNeuron(ozNeuronConfigurator, clusteredNEGCurrentSrc, normalLeakSource4)

# Temporal Integration
temporalConfig = 350 * (10 ** -3)
tempIntegration1 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron1)
tempIntegration2 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron2)
tempIntegration3 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron3)
tempIntegration4 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron4)
tempIntegration5 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron5)
tempIntegration6 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron6)
tempIntegration7 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron7)
tempIntegration8 = TemporalIntegration(temporalConfig, temporalConfigurator, ozNeuron8)

# Adder
adderForSin = Adder()
adderForLin = Adder()

# ErrorCKT
errorBlockSin = ErrorBlock(adderForSin, vinSin, 8)
errorBlockLin = ErrorBlock(adderForLin, vinLin, 8)

# LearningBlocks
LR = 0.1
learningBlock1Sin = LearningBlock(LR, tempIntegration1, errorBlockSin)
learningBlock2Sin = LearningBlock(LR, tempIntegration2, errorBlockSin)
learningBlock3Sin = LearningBlock(LR, tempIntegration3, errorBlockSin)
learningBlock4Sin = LearningBlock(LR, tempIntegration4, errorBlockSin)
learningBlock5Sin = LearningBlock(LR, tempIntegration5, errorBlockSin)
learningBlock6Sin = LearningBlock(LR, tempIntegration6, errorBlockSin)
learningBlock7Sin = LearningBlock(LR, tempIntegration7, errorBlockSin)
learningBlock8Sin = LearningBlock(LR, tempIntegration8, errorBlockSin)

learningBlock1Lin = LearningBlock(LR, tempIntegration1, errorBlockLin)
learningBlock2Lin = LearningBlock(LR, tempIntegration2, errorBlockLin)
learningBlock3Lin = LearningBlock(LR, tempIntegration3, errorBlockLin)
learningBlock4Lin = LearningBlock(LR, tempIntegration4, errorBlockLin)
learningBlock5Lin = LearningBlock(LR, tempIntegration5, errorBlockLin)
learningBlock6Lin = LearningBlock(LR, tempIntegration6, errorBlockLin)
learningBlock7Lin = LearningBlock(LR, tempIntegration7, errorBlockLin)
learningBlock8Lin = LearningBlock(LR, tempIntegration8, errorBlockLin)

# Layers
L1 = [vinSin, vinLin, preProcessBlockLin, preProcessBlockSin]
L2 = [negativePulseSynapseSin, positivePulseSynapseLin, clusteredPosCurrentSrc, clusteredNEGCurrentSrc]
L3 = [ozNeuron1, ozNeuron2, ozNeuron3, ozNeuron4, ozNeuron5, ozNeuron6, ozNeuron7, ozNeuron8]
L4 = [tempIntegration1, tempIntegration2, tempIntegration3, tempIntegration4, tempIntegration5, tempIntegration6, tempIntegration7,
      tempIntegration8]
L5 = [learningBlock1Sin, learningBlock2Sin, learningBlock3Sin, learningBlock4Sin, learningBlock5Sin, learningBlock6Sin, learningBlock7Sin,
      learningBlock8Sin]
L6 = [learningBlock1Lin, learningBlock2Lin, learningBlock3Lin, learningBlock4Lin, learningBlock5Lin, learningBlock6Lin, learningBlock7Lin,
      learningBlock8Lin]

L7 = [adderForSin, adderForLin]
L8 = [errorBlockSin, errorBlockLin]

adderForSin.setListOfSources(L5)
adderForLin.setListOfSources(L6)

layers = [L1, L2, L3, L4, L5, L6, L7, L8]

timeAxis = []
neuronsVout = {}
temporalBlockVout = {}

learningBlockVout = {}

keyToNeuronObj = {}
keyToTemporalObj = {}
keyToLRObj = {}

vinSinVals = []
vinLinVals = []
spikesVals = [[] for x in L3]
temporalSpikesVals = [[] for x in L4]
learningWeights = [[] for x in L5]

sinAdderVals = []
linAdderVals = []


errorVals = []
weightVals = []

for x in range(len(L3)):
    k = "n{}".format(x)
    neuronsVout[k] = []
    temporalBlockVout[k] = []
    learningBlockVout[k] = []

    keyToNeuronObj[k] = L3[x]
    keyToTemporalObj[k] = L4[x]
    keyToLRObj[k] = L5[x]

simResTime = ozNeuronConfigurator.getSimTimeTick()
SIMULATION_TICKS = int(SIM_TIME // simResTime)

timeAxisVal = 0
startTime = time.time()
for tick in range(SIMULATION_TICKS):
    print("\rSTEP {}/{}".format(tick, SIMULATION_TICKS))
    # sys.stdout.write()
    timeAxis.append(timeAxisVal)
    timeAxisVal += simResTime

    for l in layers:
        for obj in l:
            obj.run()

    for ko in keyToNeuronObj.keys():
        neuronsVout[ko].append(keyToNeuronObj[ko].getVoltage())
        temporalBlockVout[ko].append(keyToTemporalObj[ko].getVoltage())
        learningBlockVout[ko].append(keyToLRObj[ko].getVoltage())

    for x in range(len(L3)):
        spikesVals[x].append(L3[x].getVoltage())

    for x in range(len(L4)):
        temporalSpikesVals[x].append(L4[x].getVoltage())

    for x in range(len(L5)):
        learningWeights[x].append(L5[x].getVoltage())

    sinAdderVals.append(adderForSin.getVoltage())
    linAdderVals.append(adderForLin.getVoltage())

    vinSinVals.append(vinSin.getVoltage())
    vinLinVals.append(vinLin.getVoltage())

print("\nsimulation runtime {}".format(time.time() - startTime))


# for y in range(len(spikesVals)):
#     axs[y, 0].plot(timeAxis, spikesVals[y])
#
# for y in range(len(temporalSpikesVals)):
#     axs[y, 1].plot(timeAxis, temporalSpikesVals[y])
#
# for y in range(len(learningWeights)):
#     axs[y, 2].plot(timeAxis, learningWeights[y])


plt.subplot(2, 2, 1)
plt.plot(timeAxis, vinSinVals)

plt.subplot(2, 2, 2)
plt.plot(timeAxis, vinLinVals)

plt.subplot(2, 2, 3)
plt.plot(timeAxis, sinAdderVals)

plt.subplot(2, 2, 4)
plt.plot(timeAxis, linAdderVals)

plt.show()
