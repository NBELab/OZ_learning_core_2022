import traceback

from NeuralEmulator.Interfaces.CurrentSourceBase import CurrentSourceBase
from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase
from NeuralEmulator.Utils.Utils import getObjID


class ClusterVoltageSource(VoltageSourceBase):
    def __init__(self, listOfSources):
        self.voltage = 0
        self.sources = listOfSources

    def getVoltage(self):
        return self.voltage

    def run(self):
        self.voltage = 0
        for lsrc in self.sources:
            self.voltage += lsrc.getVoltage()


class ClusterCurrentSource(CurrentSourceBase):

    def __init__(self, listOfSources, pringLog=False):
        self.current = 0
        self.sources = listOfSources
        self.pringLog = pringLog
        ids = [getObjID(x) for x in listOfSources]
        if self.pringLog is True:
            print("ClustCurSrc {} {}".format(getObjID(self), ids))

    def getCurrent(self):
        if self.pringLog is True:
            print("ClustCurSrc {} current {}".format(getObjID(self), self.current))
        return self.current

    def run(self):
        self.current = 0
        for lsrc in self.sources:
            if self.pringLog is True:
                print("ClustCurSrc {} intputcurr {} from {}".format(getObjID(self), lsrc.getCurrent(), getObjID(lsrc)))

            self.current += lsrc.getCurrent()
