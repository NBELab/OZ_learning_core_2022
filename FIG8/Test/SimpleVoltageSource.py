from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase


class SimpleVoltageSource(VoltageSourceBase):
    def __init__(self, v=0):
        self.v = v

    def getVoltage(self):
        return self.v

    def setVoltage(self, v):
        self.v = v

    def run(self):
        pass


if __name__ == "__main__":
    simpleVoltageSource = SimpleVoltageSource()
