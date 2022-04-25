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

SIM_TIME = 1.0
NUMBER_OF_NEURONS = 8

LR = 0.5* (10 ** -3)

generator = Generator()
pulseSynapseConfigurator = PulseSynapseConfigurator()
noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
ozNeuronConfigurator = OZNeuronConfigurator()
temporalConfigurator = TemporalConfigurator()
####################################################################################


vinSin = SinSignal(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 2)
vinSin = LinearSignal(SIM_TIME,ozNeuronConfigurator.getSimTimeTick())


l1 = [vinSin]

# Sin Preprocess
preProcessBlockSin = PreprocessingBlock(vinSin)
vposPortSin = PosPreprocessingBlock(preProcessBlockSin)
vnegPortSin = NegPreprocessingBlock(preProcessBlockSin)
positivePulseSynapsex1 = PulseSynapse(vposPortSin, pulseSynapseConfigurator)
negativePulseSynapsex1 = PulseSynapse(vnegPortSin, pulseSynapseConfigurator)
l2 = [preProcessBlockSin, vposPortSin, vnegPortSin, positivePulseSynapsex1, negativePulseSynapsex1]

#l3 = Generator().generateNormalLeakSources(int(NUMBER_OF_NEURONS / 2), 700.0 * (10 ** -3), 15.0 * (10 ** -3))
l3 = Generator().generateUniformLeaks()

posNeurons = generator.generateEnsemble(positivePulseSynapsex1, l3)
negNeurons = generator.generateEnsemble(negativePulseSynapsex1, l3)
l4 = posNeurons + negNeurons


posTemporals = generator.generateTempIntegrations(80 * (10 ** -3), posNeurons)
negTemporals = generator.generateTempIntegrations(80 * (10 ** -3), negNeurons)
l5 = posTemporals + negTemporals

adderForX1 = Adder(l5)
errorBlockX1 = ErrorBlock(adderForX1, vinSin, NUMBER_OF_NEURONS)
l6 = [adderForX1, errorBlockX1]

x1LearningBlocks = generator.generateLearningBlock(LR, l5, errorBlockX1)
l7 = x1LearningBlocks
adderForX1.setListOfSources(x1LearningBlocks)
layers = [l1, l2, l3, l4, l5, l6, l7]

simResTime = ozNeuronConfigurator.getSimTimeTick()
SIMULATION_TICKS = int(SIM_TIME // simResTime)

timeAxisVal = 0
startTime = time.time()

x1LearninBlocksOutput = [[] for x in x1LearningBlocks]

neurons = [[] for n in l4]
temporals = [[] for n in l4]
lrBlocks = [[] for n in l4]

timeAxis = []
adderProbe = []
vinProb = []
sumVal = []

for tick in range(SIMULATION_TICKS):
    print("\rSTEP {}/{}".format(tick + 1, SIMULATION_TICKS))
    timeAxis.append(timeAxisVal)
    timeAxisVal += simResTime

    for layer in layers:
        for obj in layer:
            obj.run()

    adderProbe.append(adderForX1.getVoltage())
    vinProb.append(vinSin.getVoltage())

    for n in range(len(l4)):
        neurons[n].append(l4[n].getVoltage())
        temporals[n].append(l5[n].getVoltage())
        lrBlocks[n].append(x1LearningBlocks[n].getVoltage())

fig, axs = plt.subplots(8, 2)
for n in range(len(neurons)):
    axs[n, 0].plot(timeAxis, neurons[n])
    # axs[n, 1].plot(timeAxis, temporals[n])
    # axs[n, 2].plot(timeAxis, lrBlocks[n])

axs[0, 1].plot(timeAxis, vinProb)
# axs[1, 3].plot(timeAxis, adderProbe)

# fig, axs = plt.subplots(2, 2)
# axs[0, 0].plot(timeAxis, vinProb)
# axs[1, 0].plot(timeAxis, adderProbe)

plt.show()

# OUTOUT_FOLDER = r'C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\results\learning'
# OUTOUT_FILE = OUTOUT_FOLDER + "\\bounded_learning.csv"
#
# df = pd.DataFrame({'time':timeAxis,"vin":vinProb,"vout":adderProbe})
# df.to_csv(OUTOUT_FILE, header=True, index=False)
