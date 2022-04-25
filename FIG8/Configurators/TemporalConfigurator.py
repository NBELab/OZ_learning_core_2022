import json
import os
import pandas as pd
import numpy as np


class TemporalConfigurator:
    def __init__(self):
        configFileName = os.getenv('NERUSIM_CONF')
        if configFileName is None:
            raise RuntimeError("Env var NERUSIM_CONF is not define")

        confFilePath = configFileName + r"\TemporalConfigurator.json"

        if not os.path.exists(confFilePath):
            raise RuntimeError("Configuration file do not exists " + confFilePath)

        with open(confFilePath) as f:
            data = json.load(f)

            csvFile = data["currentModelPath"]
            df = pd.read_csv(csvFile)
            self.df_vin = df["vin"].to_numpy(dtype=float)
            self.df_amp = df["amp"].to_numpy(dtype=float)
            self.df_dt = df["dt"].to_numpy(dtype=float)

    def getAmpAndDtForVoltage(self, volt):
        t = np.searchsorted(self.df_vin, volt, side='right')
        amp = self.df_amp[t - 1]
        t = self.df_dt[t - 1]
        return amp, t

    def getSimTime(self):
        return 4.8809138070110005e-05


if __name__ == "__main__":
    pass
