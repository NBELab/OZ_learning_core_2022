from NeuralEmulator.Interfaces.SimBase import SimBase
from abc import ABC, abstractmethod


class LeakCurrentBase(SimBase):
    @abstractmethod
    def getCurrent(self):
        pass
