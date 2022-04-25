import os
import json
import pandas as pd
import numpy as np


class OZNeuronConfigurator:
    def __init__(self):
        configFileName = os.getenv('NERUSIM_CONF')
        if configFileName is None:
            raise RuntimeError("Env var NERUSIM_CONF is not define")

        confFilePath = configFileName + r"\OZNeuron.json"

        if not os.path.exists(confFilePath):
            raise RuntimeError("Configuration file do not exists " + confFilePath)

        data = None
        with open(confFilePath) as f:
            data = json.load(f)

        coef = data["iInCoef"]
        coef.reverse()

        self.iIncoef = data["iInCoef"]
        self.spikeWidthTime = data["spikeWidthTime"]
        self.simTime = data["simTime"]

        self.spikeRiseSamplesCount = data["spikeRiseSize"]
        self.spikeRiseCoef = data["spikeRiseCoef"]
        self.spikeRiseCoef.reverse()

        self.spikeFallSamplesCount = data["spikeFallSize"]
        self.spikeFallCoef = data["spikeFallCoef"]
        self.spikeFallCoef.reverse()

        spikeRiseVals = self.getSpikeRiseVals()
        spikeFallVals = self.getSpikeFallVals()

        fullspike = spikeRiseVals + spikeFallVals

        self.fullSpike = fullspike

        csvFile = data["currentModelPath"]

        df = pd.read_csv(csvFile)
        self.df_iIn = df["Iin"].to_numpy(dtype=float)
        self.df_freq = df["Freq"].to_numpy(dtype=float)

    def getFreqForCurrent(self, current):
        t = np.searchsorted(self.df_iIn, current, side='right')
        val = self.df_iIn[t - 1]
        return self.df_freq[t - 1]

    def getSpikeRiseVals(self):
        spikeRiseVal = []

        for spikeValIndex in range(self.spikeRiseSamplesCount):
            val = 0
            for spikeValForIndex in range(len(self.spikeRiseCoef)):
                val += self.spikeRiseCoef[spikeValForIndex] * (spikeValIndex ** (spikeValForIndex))
            spikeRiseVal.append(val)
        return spikeRiseVal

    def getSpikeFallVals(self):
        spikeRiseVal = []

        for spikeValIndex in range(self.spikeFallSamplesCount):
            val = 0
            for spikeValForIndex in range(len(self.spikeFallCoef)):
                val += self.spikeFallCoef[spikeValForIndex] * (spikeValIndex ** (spikeValForIndex))
            spikeRiseVal.append(val)
        return spikeRiseVal

    def getSpikeWidthTime(self):
        return self.spikeWidthTime

    def getSimTimeTick(self):
        return self.simTime

    def getSpikevalsList(self):
        return self.fullSpike


if __name__ == "__main__":
    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    oZNeuronConfigurator = OZNeuronConfigurator()
