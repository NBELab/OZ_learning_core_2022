from NeuralEmulator.Interfaces.SimBase import SimBase
from abc import ABC, abstractmethod


class CurrentSourceBase(SimBase):
    @abstractmethod
    def getCurrent(self):
        pass
