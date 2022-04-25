import os

from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase
import numpy as np
import matplotlib.pyplot as plt


class LinearSignal(VoltageSourceBase):
    def __init__(self, simTime, simStep):
        steps = int(simTime // simStep)

        x = np.linspace(-1, 1, steps)

        self.y = x

        self.index = 0
        self.vout = 0

    def getVoltage(self):
        return self.vout

    def run(self):
        if self.index > len(self.y):
            self.vout = self.y[-1]
        else:
            self.vout = self.y[self.index]
            self.index += 1


class StaticSource(VoltageSourceBase):
    def __init__(self, vin):
        self.vin = vin

    def getVoltage(self):
        return self.vin

    def setVoltage(self, val):
        self.vin = val

    def run(self):
        pass


class ListVoltageSource(VoltageSourceBase):

    def __init__(self, values):
        self.values = values
        self.index = 0
        self.len = len(values)

    def getVoltage(self):
        if self.index >= len(self.values):
            return self.values[-1]
        else:
            return self.values[self.index]

    def run(self):
        self.index += 1


class OscylatorRefSignal(VoltageSourceBase):

    def __init__(self, vmain, vref, factor):
        self.vmain = vmain
        self.vref = vref
        self.factor = factor
        self.vout = 0

    def run(self):
        self.vout = self.vmain.getVoltage() + self.factor * self.vref.getVoltage()

    def getVoltage(self):
        return self.vout


class PulseSource(VoltageSourceBase):
    def __init__(self, pulseStartTime, pulseWidth, pulseAmplitude, simTick=4.8809138070110005e-05):
        self.pulseStartTime = pulseStartTime
        self.pulseWidth = pulseWidth
        self.pulseAmplitude = pulseAmplitude
        self.simTick = simTick
        self.counter = 1
        self.vout = 0

    def run(self):
        ctime = self.counter * self.simTick
        if self.pulseStartTime <= ctime <= self.pulseStartTime + self.pulseWidth:
            self.vout = self.pulseAmplitude
        else:
            self.vout = 0
        self.counter += 1

    def getVoltage(self):
        return self.vout


class LinearSignalSteps(VoltageSourceBase):
    def __init__(self, simTime, simStep, holdSteps):
        self.simStep = simStep

        steps = int(simTime // simStep)

        timePerStep = int(steps // holdSteps)
        voltDeltaPerStep = 2 / holdSteps

        start = 0
        end = timePerStep

        voltage = -1

        bounds = []
        indexToVal = {}
        for x in range(holdSteps):
            xValsForStep = np.linspace(start, end, steps)
            bounds.append(xValsForStep)
            start = end
            end += timePerStep
            indexToVal[x] = voltage
            voltage += voltDeltaPerStep

        self.bounds = bounds
        self.indexToVal = indexToVal

        self.counter = 0

    def getVoltage(self):
        return self.vout

    def run(self):

        for x in range(len(self.bounds)):
            vals =self.bounds[x]
            if self.counter < vals[-1]:
                self.vout = self.indexToVal[x]
                break

        self.counter = self.counter + 1

if __name__ == "__main__":
    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    SIM_TIME = 1.0
    simResTime = OZNeuronConfigurator().getSimTimeTick()
    SIMULATION_TICKS = int(SIM_TIME // simResTime)

    vin = LinearSignalSteps(SIM_TIME, OZNeuronConfigurator().getSimTimeTick(),200)


    voutVals = []
    timeAxis = []

    timeIndex = 0
    for tick in range(SIMULATION_TICKS):
        print("\rSTEP {}/{}".format(tick + 1, SIMULATION_TICKS))
        timeAxis.append(timeIndex)
        timeIndex += simResTime
        vin.run()
        voutVals.append(vin.getVoltage())

    plt.plot(timeAxis, voutVals)
    plt.show()
