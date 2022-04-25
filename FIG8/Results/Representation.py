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
SinInput = True
vals = [[False, False], [False, True], [True, False], [True, True]]

for v in vals:
    BoundedLeaks = v[0]
    SinInput = v[1]

    for x in range(2, 10, 2):
        NUMBER_OF_NEURONS = x
        curveFolder = "Bounded" if BoundedLeaks is True else "Uniform"
        signalFolder = "Sin" if SinInput is True else "Lin"

        OUTOUT_FOLDER = "C:\\Users\\Avi\\Desktop\\IntelliSpikesLab\\Emulator\\results\\Emulator\\Representation\\{}\\{}\\{}OZ".format(curveFolder,
                                                                                                                                      signalFolder,
                                                                                                                                      NUMBER_OF_NEURONS)
        OUTOUT_FILE = OUTOUT_FOLDER + "\\{}_{}_{}OZ.xlsx".format(curveFolder, signalFolder, NUMBER_OF_NEURONS)
        OUTOUT_FILE_WEIGHTS = OUTOUT_FILE.replace(".xlsx", "_weights.xlsx")

        SIM_TIME = 1.0
        TEMPORAL_CONFIG = 150 * (10 ** -3)
        LR = 100 * (10 ** -3)

        generator = Generator()
        pulseSynapseConfigurator = PulseSynapseConfigurator()
        ozNeuronConfigurator = OZNeuronConfigurator()

        ####################################################################################

        if SinInput is True:
            vin = SinSignal(SIM_TIME, ozNeuronConfigurator.getSimTimeTick(), 2)
        else:
            vin = LinearSignal(SIM_TIME, ozNeuronConfigurator.getSimTimeTick())

        l1 = [vin]

        preProcessBlockSin = PreprocessingBlock(l1[0])

        vposPortSin = PosPreprocessingBlock(preProcessBlockSin)
        vnegPortSin = NegPreprocessingBlock(preProcessBlockSin)

        positivePulseSynapsex1 = PulseSynapse(vposPortSin, pulseSynapseConfigurator)
        negativePulseSynapsex1 = PulseSynapse(vnegPortSin, pulseSynapseConfigurator)

        l2 = [preProcessBlockSin, vposPortSin, vnegPortSin, positivePulseSynapsex1, negativePulseSynapsex1]

        if BoundedLeaks is True:
            l3 = Generator().generateBoundedLeaks()
        else:
            l3 = Generator().generateUniformLeaks()

        if int(NUMBER_OF_NEURONS / 2) != len(l3):
            n = int(NUMBER_OF_NEURONS / 2)
            l3 = l3[0:n]
            cx = 1

        posNeurons = generator.generateEnsemble(positivePulseSynapsex1, l3)
        negNeurons = generator.generateEnsemble(negativePulseSynapsex1, l3)
        l4 = posNeurons + negNeurons

        posTemporals = generator.generateTempIntegrations(TEMPORAL_CONFIG, posNeurons)
        negTemporals = generator.generateTempIntegrations(TEMPORAL_CONFIG, negNeurons)
        l5 = posTemporals + negTemporals

        adder = Adder()
        l6 = [adder]

        errorBlocks = ErrorBlock(adder, vin, NUMBER_OF_NEURONS)
        learningBlocks = generator.generateLearningBlock(LR, l5, errorBlocks)

        l7 = [errorBlocks]
        l8 = learningBlocks

        adder.setListOfSources(learningBlocks)

        layers = [l1, l2, l3, l4, l5, l6, l7, l8]

        #################################################################################

        simResTime = ozNeuronConfigurator.getSimTimeTick()
        SIMULATION_TICKS = int(SIM_TIME // simResTime)

        timeAxisVal = 0
        startTime = time.time()

        neurons = [[] for n in l4]
        temporalsResults = [[] for n in l4]
        learningSignals = [[] for n in l4]
        learningSignalsWeights = [[] for n in l4]

        timeAxis = []

        vinVals = []
        vposVals = []
        vnegVals = []
        voutVals = []
        errSignal = []

        for tick in range(SIMULATION_TICKS):
            print("\rSTEP {}/{}".format(tick + 1, SIMULATION_TICKS))
            timeAxis.append(timeAxisVal)
            timeAxisVal += simResTime

            for layer in layers:
                for obj in layer:
                    obj.run()

            vinVals.append(l1[0].getVoltage())
            vposVals.append(vposPortSin.getVoltage())
            vnegVals.append(vnegPortSin.getVoltage())
            voutVals.append(adder.getVoltage())
            errSignal.append(errorBlocks.getVoltage())

            for n in range(len(l4)):
                neurons[n].append(l4[n].getVoltage())

            for n in range(len(l5)):
                temporalsResults[n].append(l5[n].getVoltage())

            for n in range(len(l8)):
                learningSignals[n].append(l8[n].getVoltage())
                learningSignalsWeights[n].append(l8[n].getWeight())

        df = pd.DataFrame(
            {'time': timeAxis, 'input': vinVals, 'output': voutVals})
        df.to_excel(OUTOUT_FILE, index=None, header=True)

        f = {'time': timeAxis}

        for x in range(len(learningSignalsWeights)):
            k = "n{}".format(x + 1)
            f[k] = learningSignalsWeights[x]

        df = pd.DataFrame(f)

        df.to_excel(OUTOUT_FILE_WEIGHTS, index=None, header=True)
