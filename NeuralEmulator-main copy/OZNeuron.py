import os
import matplotlib.pyplot as plt

from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.Configurators.PulseSynapseConfigurator import PulseSynapseConfigurator
from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlock
from NeuralEmulator.PulseSynapse import PulseSynapse
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.VoltageSources.LinearSignal import LinearSignal, StaticSource, LinearSignalSteps


class OZNeuron(VoltageSourceBase):
    def __init__(self, ozNeuronConfigurator, synapse=None, leakCurrent=None, invertOutput=False, printLog=False):
        self.setSynapse(synapse)
        self.leakCurrent = leakCurrent
        self.configurator = ozNeuronConfigurator
        self.spikeModelValsList = ozNeuronConfigurator.getSpikevalsList()

        self.simTimeTick = ozNeuronConfigurator.getSimTimeTick()

        self.printLog = printLog

        self.inCurrent = 0
        self.outLeak = 0
        self.vout = 0

        self.simWindowIndex = -1
        self.invertOutput = invertOutput
        self.stopCalc = False

        self.freq = 0
        self.zeroPaddingCounter = 0

        self.spikeSamplesValsList = [0]

    def setLeakSource(self, leakCurrent):
        self.leakCurrent = leakCurrent

    def setSynapse(self, synapse):
        self.synapse = synapse

    def configWindow(self):
        if self.stopCalc is False:

            freq = self.__getFreq()

            if freq == self.freq:
                return

            self.freq = freq

            if freq != 0:
                self.stopCalc = True
                self.stopCalc = False

            netoSpikesTime = freq * (len(self.spikeModelValsList) * self.simTimeTick)
            notSpikeTime = 1.0 - netoSpikesTime

            tempMask = [0]

            if freq != 0:
                notSpikeAfterSpikeTime = notSpikeTime / freq if freq != 0 else 1.0

                notSpikeSamplesCount = notSpikeAfterSpikeTime // self.simTimeTick
                notSpikeSampleslist = [0 for x in range(int(notSpikeSamplesCount))]

                tempMask = notSpikeSampleslist + self.spikeModelValsList

            self.spikeSamplesValsList = tempMask
            self.simWindowIndex = 0

            if self.zeroPaddingCounter != 0:
                self.simWindowIndex = self.zeroPaddingCounter

    def __isInSpike(self):
        i = self.simWindowIndex % len(self.spikeSamplesValsList)
        val = self.spikeSamplesValsList[i] != 0
        return val

    def setVoutVal(self, i):
        i = i % len(self.spikeSamplesValsList)
        self.vout = self.spikeSamplesValsList[i]
        if self.vout == 0:
            self.zeroPaddingCounter = self.zeroPaddingCounter + 1
        else:
            self.zeroPaddingCounter = 0

    def getVoltage(self):
        if self.invertOutput is True:
            self.vout = (self.vout * -1) + 3.3

        return self.vout

    def __getIin(self):
        return self.inCurrent

    def __getILeak(self):
        return self.outLeak

    def __updateCurrents(self):
        self.inCurrent = self.synapse.getCurrent()
        self.outLeak = self.leakCurrent.getCurrent()

    def __getFreq(self):

        Isyn = self.__getIin()
        Ileak = self.__getILeak()
        f = self.getFreqForParams(Isyn, Ileak)

        return f

    def getFreqForParams(self, inCurrent, outCurrent):

        iIn = inCurrent - outCurrent

        if iIn < 0:
            iIn = 0

        freq = self.configurator.getFreqForCurrent(iIn)
        return freq

    def reset(self):
        self.simWindowIndex = 0
        self.inCurrent = 0
        self.outLeak = 0

    def run(self):
        self.simWindowIndex += 1

        inc = self.synapse.getCurrent()
        ouc = self.leakCurrent.getCurrent()

        if inc == self.inCurrent and ouc == self.outLeak:
            self.setVoutVal(self.simWindowIndex)
            return

        if not self.__isInSpike():
            self.inCurrent = inc
            self.outLeak = ouc

            self.configWindow()

        self.setVoutVal(self.simWindowIndex)


if __name__ == "__main__":
    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"
    SIM_TIME = 1.0

    vin = LinearSignal(SIM_TIME, OZNeuronConfigurator().getSimTimeTick())
    #    vin = LinearSignalSteps(SIM_TIME, OZNeuronConfigurator().getSimTimeTick(), 150)

    l1 = [vin]

    preProcessBlockSin = PreprocessingBlock(l1[0])
    vposPortSin = NegPreprocessingBlock(preProcessBlockSin)

    positivePulseSynapse = PulseSynapse(vposPortSin, PulseSynapseConfigurator())

    l2 = [preProcessBlockSin, vposPortSin, positivePulseSynapse]

    normalLeakSource = NormalLeakSource(NormalLeakSourceConfigurator(), StaticSource(670.0 * (10 ** -3)))

    ozNeuron = OZNeuron(OZNeuronConfigurator(), positivePulseSynapse, normalLeakSource)
    l3 = [normalLeakSource, ozNeuron]

    layers = [l1, l2, l3]

    simResTime = OZNeuronConfigurator().getSimTimeTick()
    SIMULATION_TICKS = int(SIM_TIME // simResTime)

    timeAxisVal = 0

    vinVals = []
    vposVals = []

    ozVout = []
    timeAxis = []
    # SIMULATION_TICKS = int(SIMULATION_TICKS // 4)

    for tick in range(SIMULATION_TICKS):
        print("Tick {}".format(tick))
        timeAxis.append(tick)
        timeAxisVal += simResTime

        for layer in layers:
            for obj in layer:
                obj.run()

        vinVals.append(l1[0].getVoltage())
        vposVals.append(vposPortSin.getVoltage())
        ozVout.append(ozNeuron.getVoltage())

    plt.figure(figsize=(18, 4))

    plt.plot(timeAxis, ozVout)
    plt.show()
