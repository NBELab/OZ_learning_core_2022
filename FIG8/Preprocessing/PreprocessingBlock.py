from NeuralEmulator.Interfaces.SimBase import SimBase
from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase

from NeuralEmulator.Test.SimpleVoltageSource import SimpleVoltageSource
from NeuralEmulator.Utils.Utils import getObjID


class PreprocessingBlock(SimBase):
    def __init__(self, voltgaeSource):
        self.voltgaeSource = voltgaeSource
        self.VPOS = 0
        self.VNEG = 0

    def getVoutPOS(self):
        return self.VPOS

    def getVoutNEG(self):
        return self.VNEG

    def run(self):
        vin = self.voltgaeSource.getVoltage()

        VPOS = -vin
        VPOS = -(VPOS + 1)
        VPOS = -(VPOS * 1.65)
        self.VPOS = VPOS

        VNEG = vin
        VNEG = -(VNEG + 1)
        VNEG = -(VNEG * 1.65)
        self.VNEG = VNEG




class PreprocessingBlockPos(SimBase):
    def __init__(self, voltgaeSource):
        self.voltgaeSource = voltgaeSource
        self.VPOS = 0
        self.VNEG = 0

        self.idi = getObjID(self)

        self.prevVolt = self.voltgaeSource.getVoltage()
        self.calcVoltage()


        print("PreprocessingBlockPos: idVin {} created".format(self.idi))

    def getVoutPOS(self):
        return self.VPOS

    def getVoutNEG(self):
        return self.VNEG

    def calcVoltage(self):
        VPOS = -self.prevVolt
        VPOS = VPOS + 1

        VPOS = VPOS * (3.3 / 1.0)
        self.VPOS = VPOS

        VNEG = self.prevVolt
        VNEG = VNEG * (3.3 / 1.0)
        self.VNEG = VNEG

        #print("PreprocessingBlockPos ID {}  VPOS {} NEG {} vin {}".format(self.idi, VPOS, VNEG, self.prevVolt))

    def run(self):
        vin = self.voltgaeSource.getVoltage()
        if vin != self.prevVolt:
            self.prevVolt = vin
            self.calcVoltage()


if __name__ == "__main__":
    vin = SimpleVoltageSource()
    p = PreprocessingBlock(vin)
    print("VIN -1")
    vin.setVoltage(-1.0)
    p.run()
    print("VPOS {} VNEG {}".format(p.getVoutPOS(), p.getVoutNEG()))

    print("VIN -1")
    vin.setVoltage(1.0)
    p.run()
    print("VPOS {} VNEG {}".format(p.getVoutPOS(), p.getVoutNEG()))
