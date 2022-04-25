from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase
from NeuralEmulator.Configurators.STDPSynapseConfigurator import STDPSynapseConfigurator
from NeuralEmulator.Utils.Utils import getObjID
from NeuralEmulator.VoltageSources.LinearSignal import ListVoltageSource


class STDPSynapse(VoltageSourceBase):

    def __init__(self, configurator, postSource=None, preSource=None, defaultWeight=2.4, printLog=False):
        self.defaultWeight = defaultWeight
        self.postSource = postSource
        self.preSource = preSource
        self.configurator = configurator
        self.weight = defaultWeight
        self.stepsCounter = 0

        self.postSpikeMask = [0, 0, 0]
        self.preSpikeMask = [0, 0, 0]

        self.preSpikeTime = 0
        self.postSpikeTime = 0

        self.isPreSpike = False
        self.isPostSpike = False

        self.learn = True
        self.printLog = printLog

    def reset(self):
        self.stepsCounter = 0

        self.postSpikeMask = [0, 0, 0]
        self.preSpikeMask = [0, 0, 0]

        self.preSpikeTime = 0
        self.postSpikeTime = 0

        self.isPreSpike = False
        self.isPostSpike = False

    def setPostSource(self, postSource):
        self.postSource = postSource

    def setPreSource(self, preSource):
        self.preSource = preSource

    def getVoltage(self):
        return self.weight

    def __isSpike(self, arr):

        if arr[1] > 0.8 and (arr[0] < arr[1] and arr[1] > arr[2]):
            if self.printLog is True:
                print("STDP {} SPIKE".format(getObjID(self)))

            return True
        else:
            return False

    def __updateIsPreSpikesFlags(self):
        # print("{}".format(self.postSpikeMask))

        if self.isPreSpike is False:
            self.isPreSpike = self.__isSpike(self.preSpikeMask)
            if self.isPreSpike is True:
                self.preSpikeTime = self.stepsCounter * self.configurator.getStepTime()

        if self.isPostSpike is False:
            self.isPostSpike = self.__isSpike(self.postSpikeMask)
            if self.isPostSpike is True:
                self.postSpikeTime = self.stepsCounter * self.configurator.getStepTime()

    def updateDeltaWeight(self):
        self.__updateIsPreSpikesFlags()

        if self.isPreSpike and self.isPostSpike:
            delta = self.postSpikeTime - self.preSpikeTime

            # if delta > 0:
            #     print("PRE before POST {}".format(delta))
            # else:
            #     print("POST before PRE {}".format(delta))

            dw = self.configurator.getDeltaWeightForDeltaTime(delta)
            self.weight += dw

            self.isPreSpike = self.isPostSpike = False
            self.preSpikeTime = 0
            self.postSpikeTime = 0

    def __appendVoltages(self, preVolt, postVolt):
        self.postSpikeMask.append(postVolt)
        self.postSpikeMask.pop(0)

        self.preSpikeMask.append(preVolt)
        self.preSpikeMask.pop(0)

    def setLearningVal(self, val):
        self.learn = val

    def run(self):
        preVolt = self.preSource.getVoltage()
        postVolt = self.postSource.getVoltage()
        self.__appendVoltages(preVolt, postVolt)
        if self.learn is True:
            self.updateDeltaWeight()
        self.stepsCounter += 1


if __name__ == "__main__":
    from scipy import signal
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    sTDPSynapseConfigurator = STDPSynapseConfigurator()

    steps = int(1.0 // sTDPSynapseConfigurator.getStepTime())

    t = np.linspace(0, 1, steps)

    posty = np.abs(signal.sawtooth(2 * np.pi * 5.5 * t))
    prey = np.abs(signal.sawtooth(2 * np.pi * 5.0 * t))

    n1Post = ListVoltageSource(posty)
    n2Pre = ListVoltageSource(prey)

    sTDPSynapse = STDPSynapse(sTDPSynapseConfigurator,n1Post, n2Pre)
    weights = set()
    for x in range(steps):
        n1Post.run()
        n2Pre.run()
        sTDPSynapse.run()
        weights.add(sTDPSynapse.getVoltage())

    print(weights)
    plt.plot(t, posty, 'g', label='post')
    plt.plot(t, prey, 'r--', label='pre')

    plt.show()
