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
from NeuralEmulator.Utils.Utils import playSound, rasterplotFromCsv
from NeuralEmulator.VoltageSources.LinearSignal import LinearSignal, OscylatorRefSignal, PulseSource, LinearSignalSteps
from NeuralEmulator.VoltageSources.SinSignal import SinSignal, SquaredSin

os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

BoundedLeaks = True
NUMBER_OF_NEURONS = 8
curveFolder = "Bounded"

OUTOUT_FOLDER = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\results\Emulator\2D"
OUTOUT_FILE = OUTOUT_FOLDER + "\\{}_{}_{}OZ.xlsx".format(curveFolder, "learn", NUMBER_OF_NEURONS)
OUTOUT_FILE_WEIGHTS = OUTOUT_FILE.replace(".xlsx", "_weights.xlsx")


SIM_TIME = 1.0
TEMPORAL_CONFIG = 150 * (10 ** -3)
LR = 100 * (10 ** -3)

generator = Generator()
pulseSynapseConfigurator = PulseSynapseConfigurator()
ozNeuronConfigurator = OZNeuronConfigurator()

####################################################################################

vinSin = SinSignal(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 1.5)
vinLin = LinearSignal(1.0, ozNeuronConfigurator.getSimTimeTick())
l1 = [vinSin, vinLin]

# Sin Preprocess
preProcessBlockSin = PreprocessingBlock(vinSin)
vposPortSin = PosPreprocessingBlock(preProcessBlockSin)
vnegPortSin = NegPreprocessingBlock(preProcessBlockSin)

# Lin Preprocess
preProcessBlockLin = PreprocessingBlock(vinLin)
vposPortLin = PosPreprocessingBlock(preProcessBlockSin)
vnegPortLin = NegPreprocessingBlock(preProcessBlockSin)

l2 = [preProcessBlockSin, vposPortSin, vnegPortSin, preProcessBlockLin, vposPortLin, vnegPortLin]

# Synapses
positivePulseSynapseSin = PulseSynapse(vposPortSin, pulseSynapseConfigurator)
negativePulseSynapseSin = PulseSynapse(vnegPortSin, pulseSynapseConfigurator)

positivePulseSynapseLin = PulseSynapse(vposPortLin, pulseSynapseConfigurator)
negativePulseSynapseLin = PulseSynapse(vnegPortLin, pulseSynapseConfigurator)

# Clustered Sources
clusteredPosCurrentSrc = ClusterCurrentSource([positivePulseSynapseSin, positivePulseSynapseLin])
clusteredNEGCurrentSrc = ClusterCurrentSource([negativePulseSynapseSin, negativePulseSynapseLin])

l3 = [positivePulseSynapseSin, negativePulseSynapseSin, positivePulseSynapseLin, negativePulseSynapseLin, clusteredPosCurrentSrc,
      clusteredNEGCurrentSrc]

if BoundedLeaks is True:
    l4 = Generator().generateBoundedLeaks()
else:
    l4 = Generator().generateUniformLeaks()

posNeurons = generator.generateEnsemble(clusteredPosCurrentSrc, l4)
negNeurons = generator.generateEnsemble(clusteredNEGCurrentSrc, l4)
l5 = posNeurons + negNeurons

posTemporals = generator.generateTempIntegrations(TEMPORAL_CONFIG, posNeurons)
negTemporals = generator.generateTempIntegrations(TEMPORAL_CONFIG, negNeurons)

l6 = posTemporals + negTemporals

sinAdder = Adder()
linAdder = Adder()
l7 = [sinAdder, linAdder]

errorBlockSin = ErrorBlock(sinAdder, vinSin, NUMBER_OF_NEURONS)
errorBlockLin = ErrorBlock(linAdder, vinLin, NUMBER_OF_NEURONS)

l8 = [errorBlockSin, errorBlockLin]

sinLearningBlocks = generator.generateLearningBlock(LR, l6, errorBlockSin)
linLearningBlocks = generator.generateLearningBlock(LR, l6, errorBlockLin)

l9 = sinLearningBlocks+ linLearningBlocks

sinAdder.setListOfSources(sinLearningBlocks)
linAdder.setListOfSources(linLearningBlocks)

layers = [l1, l2, l3, l4, l5, l6, l7, l8, l9]

#################################################################################

simResTime = ozNeuronConfigurator.getSimTimeTick()
SIMULATION_TICKS = int(SIM_TIME // simResTime)

timeAxisVal = 0

timeAxis = []

vinSinVals = []
vinLinVals = []

voutSin = []
voutLin = []

for tick in range(SIMULATION_TICKS):
    print("\rSTEP {}/{}".format(tick + 1, SIMULATION_TICKS))
    timeAxis.append(timeAxisVal)
    timeAxisVal += simResTime

    for layer in layers:
        for obj in layer:
            obj.run()

    vinSinVals.append(vinSin.getVoltage())
    vinLinVals.append(vinLin.getVoltage())
    voutSin.append(sinAdder.getVoltage())
    voutLin.append(linAdder.getVoltage())

df = pd.DataFrame(
    {'time': timeAxis, 'X1': vinSinVals, 'X2': vinLinVals,"X1OUT":voutSin,"X2OUT":voutLin})

df.to_excel(OUTOUT_FILE, index=None, header=True)

# plt.subplot(2, 2, 1)
# plt.plot(timeAxis, vinSinVals)
#
# plt.subplot(2, 2, 2)
# plt.plot(timeAxis, vinLinVals)
#
# plt.subplot(2, 2, 3)
# plt.plot(timeAxis, voutSin)
#
# plt.subplot(2, 2, 4)
# plt.plot(timeAxis, voutLin)
#
# plt.show()