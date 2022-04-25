from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase


class PosPreprocessingBlock(VoltageSourceBase):
    def __init__(self, preprocessingBlock):
        self.preprocessingBlock = preprocessingBlock

    def getVoltage(self):
        v = self.preprocessingBlock.getVoutPOS()
        return v

    def run(self):
        pass
