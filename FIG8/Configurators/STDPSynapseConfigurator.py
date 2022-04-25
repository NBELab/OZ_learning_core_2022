import os
import pandas
import numpy as np


class STDPSynapseConfigurator:
    def __init__(self):
        configFileName = os.getenv('NERUSIM_CONF')
        if configFileName is None:
            raise RuntimeError("Env var NERUSIM_CONF is not define")

        confFilePath = configFileName + r"\STDPSynapse.csv"

        if not os.path.exists(confFilePath):
            raise RuntimeError("Configuration file do not exists " + confFilePath)

        df = pandas.read_csv(confFilePath)
        self.df_delta = df["delta"].to_numpy(dtype=float) * (10 ** 3)
        self.df_weight = df["weight"].to_numpy(dtype=float)

    def getDeltaWeightForDeltaTime(self, dt):
        t = np.searchsorted(self.df_delta, dt, side='right')
        return self.df_weight[t - 1]

    def getStepTime(self):
        return 4.8809138070110005e-05
