from NeuralEmulator.Interfaces.VoltageSourceBase import VoltageSourceBase
from NeuralEmulator.Utils.Utils import getObjID


class LearningBlock(VoltageSourceBase):
    def __init__(self, LR, temporalSignal, errorSignal=None):
        self.LR = LR
        self.errorSignal = errorSignal
        self.temporalSignal = temporalSignal
        self.vout = 0
        self.weight = 0.0
        self.learn = True

    def setErrorBlock(self,errorSignal):
        self.errorSignal = errorSignal

    def setLearningVal(self,val):
        self.learn = val

    def __calcVout(self):
        if self.learn is True:
            deltaW = self.errorSignal.getVoltage() * self.temporalSignal.getVoltage() * self.LR
            self.weight = self.weight + deltaW

        t = self.temporalSignal.getVoltage()
        # print("LearningBlock {} Vin {} from {} weight {}".format(getObjID(self),t,getObjID(self.temporalSignal),self.weight))
        self.vout = self.temporalSignal.getVoltage() * self.weight

    def getVoltage(self):
        return self.vout

    def getWeight(self):
        return self.weight

    def run(self):
        self.__calcVout()
