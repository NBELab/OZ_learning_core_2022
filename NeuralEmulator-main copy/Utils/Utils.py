import glob

from numba import njit, vectorize, float64, int64
import time
import numpy as np
from playsound import playsound
import matplotlib.pyplot as plt
from nengo.utils.matplotlib import rasterplot

def getFreqForSpikesVec(voutIndexToVal):
    spikeCount = 0

    for x in range(len(voutIndexToVal)):
        if voutIndexToVal[x] < 3.0:
            continue

        if x - 1 < 0 or x + 1 >= len(voutIndexToVal):
            continue

        try:
            if voutIndexToVal[x] > voutIndexToVal[x - 1] and voutIndexToVal[x] > voutIndexToVal[x + 1]:
                spikeCount = spikeCount + 1

        except:
            print("Exception")

    return spikeCount


@njit
def getValueFromPoly(coef, len, x):
    value = 0
    for c in range(len):
        value = value + coef[c] * (x ** c)

    return value


def SpiceToFloat(val):
    if 'm' in val:
        val = val.replace("m", "")
        retVal = float(val)
        retVal = retVal * float(10 ** (-3))
        return retVal
    if 'µ' in val:
        val = val.replace("µ", "")
        retVal = float(val)
        retVal = retVal * float(10 ** (-6))
        return retVal
    if 'n' in val:
        val = val.replace("n", "")
        retVal = float(val)
        retVal = retVal * float(10 ** (-9))
        return retVal

    retVal = float(val)
    return retVal


def getObjID(obj):
    idi = id(obj)
    idif = idi * (10 ** -5)
    idi = int((idif - int(idif)) * 10 ** 5)
    return idi


@njit
def getExpDecayFunc(N, tau, simStepTime):
    samples = int(tau // simStepTime)
    samples = samples * 60
    t = np.linspace(0, 1, samples)
    window = N * np.exp(-t / tau)
    return window


def playSound():
    playsound('C:\\Users\\Avi\\Desktop\\PyProj\\AviBus\\sound\\sound.mp3')


def rasterplotFromCsv(CIRCUIT_FOLDER):
    filesToRead = glob.glob(CIRCUIT_FOLDER + r'\*.csv')

    for res in filesToRead:
        time = []
        spikes = np.full((1, 8), 0)
        print(res)
        with open(res, 'r') as in_file:
            fl = in_file.readline()
            fl = fl.split(",")
            for line in in_file:

                line = line.split(',')

                time.append(float(line[0]))

                line = line[1:]
                tempSikes = []
                for s in line:
                    spikeVal = float(s)
                    if spikeVal < 3:
                        spikeVal = 0
                    else:
                        spikeVal = 1

                    tempSikes.append(spikeVal)

                tempSikes = np.asarray(tempSikes).reshape(1, 8)

                spikes = np.concatenate((spikes, tempSikes), axis=0)

            time = np.asarray(time)
            spikes = np.delete(spikes, 0, 0)
            plt.figure(figsize=(20, 10))

            rasterplot(time, spikes)
            plt.xlim(0, 1)
            plt.xlabel("Time (s)")
            plt.ylabel("Neuron")
            imgName = res.replace(".csv", ".png")

            plt.savefig(imgName)

if __name__ == "__main__":
    playSound()

    # coef = [x + 1 for x in range(2000)]
    # coef = np.array(coef)
    # l = coef.shape[0]
    # x = 1
    #
    # start = time.time()
    # getValueFromPoly(coef, l, x)
    # print("First Time elapsed:", time.time() - start)
    #
    # start = time.time()
    # getValueFromPoly(coef, l, x)
    # print("Second Time elapsed:", time.time() - start)
