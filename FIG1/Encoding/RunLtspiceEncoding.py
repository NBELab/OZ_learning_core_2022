import ltspice
import glob
from subprocess import Popen, PIPE
import numpy as np
import matplotlib.pyplot as plt
from nengo.utils.matplotlib import rasterplot
import csv
import pandas as pd

LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
CIRCUIT_FOLDER = r"C:\Users\Avi\Desktop\IEEGIT\TBioCAS2021\FIG1\Encoding\*\*"


def RunSim():
    circuits = glob.glob(CIRCUIT_FOLDER + r'\*.asc')

    for ckt in circuits:
        print("-I- Run sim {}".format(ckt))
        process = Popen([LTSPICE_PATH, "-b", "-ascii", "-RUN", ckt], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        print("-I- Done")


def ConvertRAWtoTXT():
    rawFiles = glob.glob(CIRCUIT_FOLDER + r'\*.raw')
    for raw in rawFiles:
        if ".op" in raw:
            continue

        print("-I- Converting {} to TXT".format(raw))

        txtFile = raw.replace(".raw", ".txt")

        with open(txtFile, mode='w', newline='') as out_file:

            l = ltspice.Ltspice(raw)
            l.parse()

            spikesNumber = sum(1 for x in l.variables if "spikes" in x)

            header = "time"
            for x in range(spikesNumber):
                header += " spikes{}".format(x + 1)

            out_file.write(header + "\n")

            for i in range(l.case_count):
                time = l.get_time(i)

                spikes = []
                for x in range(spikesNumber):
                    t = l.getData('V(spikes{})'.format(x + 1), i)
                    spikes.append(t)

                for index in range(time.shape[0]):
                    row = [time[index]]
                    for spike in spikes:
                        row.append(spike[index])
                    row = [str(x) for x in row]
                    row = " ".join(row) + "\n"
                    out_file.write(row)


def toFloat(val):
    if 'm' in val:
        val = val.replace("m", "")
        val = float(val)
        val = val / 1000.0
        return val

    val = float(val)
    return val


def HandleSample(voutIndexToVal):
    retMapVals = {}

    for voutIndex in voutIndexToVal.keys():
        outputVals = voutIndexToVal[voutIndex]
        spikeCount = 0

        for x in range(len(outputVals)):
            if outputVals[x] < 1.0:
                continue

            if x - 1 < 0 or x + 1 >= len(outputVals):
                continue

            try:
                if outputVals[x] > outputVals[x - 1] and outputVals[x] > outputVals[x + 1]:
                    spikeCount = spikeCount + 1

            except:
                print("Exception")

        retMapVals[voutIndex] = spikeCount
    return retMapVals


def ConvertTXTtoCSV():
    filesToRead = glob.glob(CIRCUIT_FOLDER + r'\*.txt')

    for res in filesToRead:
        print("-I- Converting {} to CSV".format(res))
        csvFile = res.replace(".txt", ".csv")
        xlsxFile = res.replace(".txt", ".xlsx")
        with open(res, 'r') as in_file:
            header = in_file.readline().replace("\n", " ").replace("\t", " ").strip().split()

            with open(csvFile, mode='w', newline='') as out_file:
                writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(header)

                for line in in_file:
                    line = line.split()
                    writer.writerow(line)

        read_file = pd.read_csv(csvFile)
        read_file.to_excel(xlsxFile, index=None, header=True)


def ConvertTXTtoEventIMG():
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
            imgName = res.replace(".csv", ".png")

            plt.savefig(imgName)


RunSim()
ConvertRAWtoTXT()
ConvertTXTtoCSV()
ConvertTXTtoEventIMG()
