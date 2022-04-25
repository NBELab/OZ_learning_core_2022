import os
import json
import pandas as pd
import numpy as np


class PulseSynapseConfigurator:
    def __init__(self):
        configFileName = os.getenv('NERUSIM_CONF')
        if configFileName is None:
            raise RuntimeError("Env var NERUSIM_CONF is not define")

        confFilePath = configFileName + r"\PulseSynapse.json"

        if not os.path.exists(confFilePath):
            raise RuntimeError("Configuration file do not exists " + confFilePath)

        data = None
        with open(confFilePath) as f:
            data = json.load(f)

        coef = data["ioutCoef"]
        coef.reverse()

        self.iIncoef = data["ioutCoef"]

        csvFile = data["currentModelPath"]
        df = pd.read_csv(csvFile)
        self.df_vin = df["vin"].to_numpy(dtype=float)
        self.df_iout = df["iout"].to_numpy(dtype=float)

    def getCurrentForVoltage(self, volt):
        t = np.searchsorted(self.df_vin, volt, side='right')
        val = self.df_iout[t - 1]
        return val

    def getCoef(self):
        return self.iIncoef


if __name__ == "__main__":
    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"
    y = PulseSynapseConfigurator()
