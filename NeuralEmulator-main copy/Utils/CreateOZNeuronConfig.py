import pandas as pd
import matplotlib.pyplot as plt
import numpy
from sklearn.metrics import r2_score
import json

FILE = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\FreqAsIin\OZ_8_bounded_curves.csv"
OUTPUT_FILE = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config\OZNeuron.json"

df = pd.read_csv(FILE)
x = df.iloc[:, 0].tolist()
y = df.iloc[:, 1].tolist()

data = {}

data["spikeWidth"] = 3.0 * 10.0 ** (-3)
data["simTime"] = 0.004880913807011 * 10.0 ** (-2)

with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4)
