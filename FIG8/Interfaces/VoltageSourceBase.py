from NeuralEmulator.Interfaces.SimBase import SimBase
from abc import abstractmethod


class VoltageSourceBase(SimBase):
    @abstractmethod
    def getVoltage(self):
        pass
