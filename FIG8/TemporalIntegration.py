from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.Configurators.PulseSynapseConfigurator import PulseSynapseConfigurator
from NeuralEmulator.Configurators.TemporalConfigurator import TemporalConfigurator
from NeuralEmulator.Interfaces.SimBase import SimBase
import numpy as np

from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from NeuralEmulator.OZNeuron import OZNeuron
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Preprocessing.PosPreprocessingBlock import PosPreprocessingBlock
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlock
from NeuralEmulator.PulseSynapse import PulseSynapse
from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource

import matplotlib.pyplot as plt

from NeuralEmulator.Utils.Utils import getObjID, getExpDecayFunc

OUTOUT_FOLDER = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\temporal"
OUTOUT_FILE = OUTOUT_FOLDER + "\\curves.csv"


class TemporalIntegration(VoltageSourceBase):
    def __init__(self, vConf, configurator, ozNeuron):
        self.configurator = configurator
        self.vConf = vConf
        amp, dt = configurator.getAmpAndDtForVoltage(vConf)
        self.spikeAmp = amp
        self.decayTime = dt

        self.ozNeuron = ozNeuron
        self.vout = 0
        self.index = 0
        self.window = []
        self.spikeMask = [0, 0, 0]
        self.spikeMaskIndex = 0

    def reset(self):
        self.vout = 0
        self.index = 0
        self.window = []
        self.spikeMask = [0, 0, 0]
        self.spikeMaskIndex = 0

    def getVoltage(self):
        # print("-I- TemporalIntegration {} VOUT {}".format(getObjID(self),self.vout))
        return self.vout

    def __appendVin(self, vin):
        self.spikeMask.append(vin)
        self.spikeMask.pop(0)

    def __isSpike(self):

        if self.spikeMask[1] > 3.0 and (self.spikeMask[0] < self.spikeMask[1] and self.spikeMask[1] > self.spikeMask[2]):
            return True
        else:
            return False

    def setPSCFilterTime(self, time):
        self.decayTime = time

    def __spikeIn(self):
        self.vout = self.vout + self.spikeAmp

        if self.vout > 3.3:
            self.vout = 3.3

        N, tau = self.vout, self.decayTime
        simStepTime = self.configurator.getSimTime()

        samples = int(tau // simStepTime)
        samples = samples *10

        maxTime = 5 * tau

        t = np.linspace(0, maxTime, samples)

        self.window = N * np.exp(-t / tau)

        self.index = 0
        self.spikeMask = [0, 0, 0]
        self.spikeMapIndex = 0

    def updateVout(self):
        if len(self.window) == 0 or self.index > len(self.window) - 1:
            self.vout = 0
        else:
            self.vout = self.window[self.index]
            if self.vout > 3.3:
                self.vout = 3.3

            self.index += 1

    def run(self):
        currentVoltage = self.ozNeuron.getVoltage()

        self.__appendVin(currentVoltage)

        if self.__isSpike():
            self.__spikeIn()
        else:
            self.updateVout()


if __name__ == "__main__":
    import os

    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    pulseSynapseConfigurator = PulseSynapseConfigurator()
    noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
    ozNeuronConfigurator = OZNeuronConfigurator()
    temporalConfigurator = TemporalConfigurator()

    # vin
    vin = SimpleVoltageSource()
    preProcessBlock = PreprocessingBlock(vin)
    vposPort = PosPreprocessingBlock(preProcessBlock)
    vnegPort = NegPreprocessingBlock(preProcessBlock)

    # Synapse
    positivePulseSynapse = PulseSynapse(vposPort, pulseSynapseConfigurator)

    # Leaks
    normalLeakSource1 = NormalLeakSource(noramalLeakSourceConfigurator, SimpleVoltageSource(750.0 * (10 ** -3)))

    # Neurons
    ozNeuron1 = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, normalLeakSource1)

    # Integration
    temporalIntegration = TemporalIntegration(150 * (10 ** -3), temporalConfigurator, ozNeuron1)

    # Layers
    L1 = [vin, preProcessBlock, vposPort, vnegPort]
    L2 = [positivePulseSynapse, normalLeakSource1]
    L3 = [ozNeuron1]
    L4 = [temporalIntegration]

    layers = [L1, L2, L3, L4]

    SIM_TIME = 1.0
    simResTime = ozNeuronConfigurator.getSimTimeTick()
    numberOfTicksPerOneSec = int(SIM_TIME // simResTime)

    ozVout = []
    temporalVout = []
    timeVec = []

    currentTime = 0

    for t in range(numberOfTicksPerOneSec):

        vin.setVoltage(190 * (10 ** -3))
        for l in layers:
            for obj in l:
                obj.run()

        ozVout.append(ozNeuron1.getVoltage())
        temporalVout.append(temporalIntegration.getVoltage())
        timeVec.append(currentTime)
        currentTime += simResTime

    plt.plot(timeVec, ozVout)
    plt.plot(timeVec, temporalVout)

    plt.show()
