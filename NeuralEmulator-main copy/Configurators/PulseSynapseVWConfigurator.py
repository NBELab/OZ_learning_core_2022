import os
import json
import pandas as pd
import numpy as np


class PulseSynapseVWConfigurator:
    def __init__(self):
        configFileName = os.getenv('NERUSIM_CONF')
        if configFileName is None:
            raise RuntimeError("Env var NERUSIM_CONF is not define")

        confFilePath = configFileName + r"\PulseSynapseVW.json"

        if not os.path.exists(confFilePath):
            raise RuntimeError("Configuration file do not exists " + confFilePath)

        with open(confFilePath) as f:
            data = json.load(f)

            csvFile = data["currentModelPath"]
            df = pd.read_csv(csvFile)
            self.df_vin = df["VIN"].to_numpy(dtype=float)
            self.df_vw = df["VW"].to_numpy(dtype=float)
            self.df_iout = df["IOUT"].to_numpy(dtype=float)

            self.vwToVinToIout = {}

            for idx in range(self.df_vw.shape[0]):
                vw = self.df_vw[idx]

                if vw not in self.vwToVinToIout:
                    self.vwToVinToIout[vw] = ([], [])
                    self.vwToVinToIout[vw][0].append(self.df_vin[idx])
                    self.vwToVinToIout[vw][1].append(self.df_iout[idx])
                else:
                    self.vwToVinToIout[vw][0].append(self.df_vin[idx])
                    self.vwToVinToIout[vw][1].append(self.df_iout[idx])

    def getCurrentForVoltage(self, vin, vw):
        vw = round(vw, 2)

        if vw > 3.3:
            vw = 3.3

        tup = self.vwToVinToIout[vw]
        t = np.searchsorted(tup[0], vin, side='right')
        val = tup[1][t - 1]
        return val


if __name__ == "__main__":
    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"
    y = PulseSynapseVWConfigurator()
    t = y.getCurrentForVoltage(0.01, 0)
