import numpy as np

from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase


class SinSignal(VoltageSourceBase):
    def __init__(self, simulationTime, stepTime, frequency=1):
        inc = int(simulationTime // stepTime)

        vals = [0]

        for x in range(1, inc):
            vals.append(vals[x - 1] + stepTime)

        x = np.array(vals)
        self.voutMask = np.sin(2 * np.pi * frequency * x)
        self.index = -1

    def run(self):
        self.index = self.index + 1

    def getVoltage(self):
        if self.index > len(self.voutMask):
            return 0
        else:
            return self.voutMask[self.index]


class SquaredSin(VoltageSourceBase):

    def __init__(self, sinSignalVoltageSource):
        self.sinSignalVoltageSource = sinSignalVoltageSource
        self.voltage = 0

    def getVoltage(self):
        return self.voltage

    def run(self):
        self.voltage = self.sinSignalVoltageSource.getVoltage() * self.sinSignalVoltageSource.getVoltage()



if __name__ == "__main__":
    sinSignal = SinSignal(1, 4.8809138070110005e-05, 2)
