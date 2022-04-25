import os
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd

from NeuralEmulator.Adder import Adder
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
from NeuralEmulator.Utils.NeuronsGenerator import NeuronsGenerator
from NeuralEmulator.VoltageSources.SinSignal import SinSignal, SquaredSin

OUTOUT_FILE = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\Learning\lr.csv"

os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

SIM_TIME = 1.0

pulseSynapseConfigurator = PulseSynapseConfigurator()
noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
ozNeuronConfigurator = OZNeuronConfigurator()
temporalConfigurator = TemporalConfigurator()

# VIN
vin = SinSignal(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 2)
vref = SquaredSin(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 2)

preProcessBlock = PreprocessingBlock(vin)
vposPort = PosPreprocessingBlock(preProcessBlock)
vnegPort = NegPreprocessingBlock(preProcessBlock)

# Synapses
positivePulseSynapse = PulseSynapse(vposPort, pulseSynapseConfigurator)
negativePulseSynapse = PulseSynapse(vnegPort, pulseSynapseConfigurator)

# Leak
normalLeakSource1 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(784.0 * (10 ** -3)))
normalLeakSource2 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(770.0 * (10 ** -3)))
normalLeakSource3 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(755.0 * (10 ** -3)))
normalLeakSource4 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(735.0 * (10 ** -3)))

# Neuron
ozNeuron1 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource1)
ozNeuron2 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource2)
ozNeuron3 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource3)
ozNeuron4 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource4)

ozNeuron5 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource1)
ozNeuron6 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource2)
ozNeuron7 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource3)
ozNeuron8 = OZNeuron(ozNeuronConfigurator, negativePulseSynapse, normalLeakSource4)

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
adder = Adder()

# ErrorCKT
errorBlock = ErrorBlock(adder, vin, 8)

# LearningBlocks
LR = 0.1
learningBlock1 = LearningBlock(LR, tempIntegration1, errorBlock)
learningBlock2 = LearningBlock(LR, tempIntegration2, errorBlock)
learningBlock3 = LearningBlock(LR, tempIntegration3, errorBlock)
learningBlock4 = LearningBlock(LR, tempIntegration4, errorBlock)
learningBlock5 = LearningBlock(LR, tempIntegration5, errorBlock)
learningBlock6 = LearningBlock(LR, tempIntegration6, errorBlock)
learningBlock7 = LearningBlock(LR, tempIntegration7, errorBlock)
learningBlock8 = LearningBlock(LR, tempIntegration8, errorBlock)

# Layers
L1 = [vin, vref, preProcessBlock]
L2 = [negativePulseSynapse, positivePulseSynapse]
L3 = [ozNeuron1, ozNeuron2, ozNeuron3, ozNeuron4, ozNeuron5, ozNeuron6, ozNeuron7, ozNeuron8]
L4 = [tempIntegration1, tempIntegration2, tempIntegration3, tempIntegration4, tempIntegration5, tempIntegration6, tempIntegration7,
      tempIntegration8]
L5 = [learningBlock1, learningBlock2, learningBlock3, learningBlock4, learningBlock5, learningBlock6, learningBlock7, learningBlock8]

L6 = [adder]
L7 = [errorBlock]

adder.setListOfSources(L5)

layers = [L1, L2, L3, L4, L5, L6, L7]

timeAxis = []
neuronsVout = {}
temporalBlockVout = {}

learningBlockVout = {}

keyToNeuronObj = {}
keyToTemporalObj = {}
keyToLRObj = {}

vinVals = []
spikesVals = [[] for x in L3]
temporalSpikesVals = [[] for x in L4]
learningWeights = [[] for x in L5]
adderVals = []
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

    adderVals.append(adder.getVoltage())
    vinVals.append(vin.getVoltage())

print("\nsimulation runtime {}".format(time.time() - startTime))

fig, axs = plt.subplots(8, 4)

for y in range(len(spikesVals)):
    axs[y, 0].plot(timeAxis, spikesVals[y])

for y in range(len(temporalSpikesVals)):
    axs[y, 1].plot(timeAxis, temporalSpikesVals[y])

for y in range(len(learningWeights)):
    axs[y, 2].plot(timeAxis, learningWeights[y])

axs[1, 3].plot(timeAxis, vinVals)
axs[0, 3].plot(timeAxis, adderVals)

plt.show()
