from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase


class NegPreprocessingBlock(VoltageSourceBase):
    def __init__(self, preprocessingBlock):
        self.preprocessingBlock = preprocessingBlock

    def getVoltage(self):
       # return self.preprocessingBlock.getVoutNEG()+1

        return self.preprocessingBlock.getVoutNEG()

    def run(self):
        pass
