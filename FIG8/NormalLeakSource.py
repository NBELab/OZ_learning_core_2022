from NeuralEmulator.Interfaces.CurrentSourceBase import CurrentSourceBase
from NeuralEmulator.Utils.Utils import getValueFromPoly
import numpy as np

from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource
from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator


class NormalLeakSource(CurrentSourceBase):
    def __init__(self, configurator, vin=None):
        self.vin = vin
        self.cacheVoltage = vin.getVoltage()
        self.current = 0
        self.coef = np.array(configurator.getCoef())
        self.configurator = configurator
        self.__calcCurrent()

    def getCurrent(self):
        return self.current

    def setVoltageSource(self, vin):
        self.vin = vin

    def __calcCurrent(self):
        self.current = self.configurator.getCurrentForVoltage(self.cacheVoltage)

    def run(self):
        v = self.vin.getVoltage()
        if self.cacheVoltage != v:
            self.cacheVoltage = v
            self.__calcCurrent()


if __name__ == "__main__":
    import os

    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    vlk = SimpleVoltageSource(780 * (10 ** -3))
    noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
    normalLeakSource = NormalLeakSource(vlk, noramalLeakSourceConfigurator)
    normalLeakSource.run()
    print(normalLeakSource.getCurrent())
