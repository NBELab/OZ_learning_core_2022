from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase


class Adder(VoltageSourceBase):
    def __init__(self, listOfSources=None):
        self.listOfSources = listOfSources
        self.vout = 0

    def setListOfSources(self, listOfSources):
        self.listOfSources = listOfSources

    def run(self):
        self.vout = 0
        for src in self.listOfSources:
            self.vout = self.vout + src.getVoltage()
        if self.vout > 3.3:
            self.vout = 3.3

    def getVoltage(self):
        return self.vout
