from NeuralEmulator.Interfaces.SimBase import SimBase
from abc import abstractmethod


class SynapseBase(SimBase):
    @abstractmethod
    def getCurrent(self):
        pass
