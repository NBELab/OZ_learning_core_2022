import glob
import numpy as np
import matplotlib.pyplot as plt
from nengo.utils.matplotlib import rasterplot



FOLDER_PATH = r"C:\Users\Avi\Desktop\IntelliSpikesLab\IEEE\FIG1\Encoding\*\*"
FILE_PATH = FOLDER_PATH + '\\*.csv'

filesToRead = glob.glob(FILE_PATH)

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
                if spikeVal < 2.9:
                    spikeVal = 0
                else:
                    spikeVal = 3

                tempSikes.append(spikeVal)

            tempSikes = np.asarray(tempSikes).reshape(1, 8)

            spikes = np.concatenate((spikes, tempSikes), axis=0)

    time = np.asarray(time)
    spikes = np.delete(spikes, 0, 0)
    plt.figure(figsize=(20, 5))

    rasterplot(time, spikes)
    plt.xlim(0, 1)
    plt.xlabel("Time (s)")
    plt.ylabel("Neuron")
    plt.show()
