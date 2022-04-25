import csv
import pandas as pd

from scipy import signal

from NeuralEmulator.Utils.Utils import SpiceToFloat
import matplotlib.pyplot as plt

FILE_PATH = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\temporal\OZ_8_pos_curves.txt"
OUT_FILE = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\temporal\OZ_8_pos_curves.csv"

def HandleSample(timeVals, voutVals):
    maxValue = max(voutVals)
    indexMax = voutVals.index(maxValue)
    semiVals = voutVals[indexMax:]
    minValue = min(semiVals)
    minIndex = voutVals.index(minValue, indexMax)

    time = float(timeVals[minIndex]) - float(timeVals[indexMax])
    return maxValue, time


with open(FILE_PATH, 'r') as in_file:
    vinToAmpAndTime = {"vin": [], "amp": [], "dt": []}
    voutVals = []
    timeVals = []

    fl = in_file.readline()
    f2 = in_file.readline()
    splittedLine = f2.split()
    preVin = SpiceToFloat(splittedLine[2].split("=")[1])

    for line in in_file:
        line = line.split()

        if "Step" in line:
            amp, t = HandleSample(timeVals, voutVals)
            vinToAmpAndTime["vin"].append(preVin)
            vinToAmpAndTime["amp"].append(amp)
            vinToAmpAndTime["dt"].append(t)

            preVin = SpiceToFloat(line[2].split("=")[1])
            voutVals = []
            timeVals = []
        else:
            line = [SpiceToFloat(x) for x in line]
            voutVals.append(line[1])
            timeVals.append(line[0])

    df = pd.DataFrame.from_dict(vinToAmpAndTime)
    df.to_csv(OUT_FILE, index=False)

    print("asd")

if __name__ == "__main__":
    import numpy as np
    N, tau = 0.6254001*2, 0.117523759268736

    # Maximum time to consider (s)
    tmax = 1
    # A suitable grid of time points, and the exponential decay itself
    t = np.linspace(0, tmax, 1000)
    y = N * np.exp(-t/tau)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(t, y)
    plt.show()