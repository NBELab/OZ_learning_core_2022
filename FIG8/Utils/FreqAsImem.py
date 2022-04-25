import glob
import csv
from NeuralEmulator.Utils.Utils import SpiceToFloat
from numba import jit, njit
import time
from scipy import signal


FOLDER_PATH = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\FreqAsIin"

FILE_PATH = FOLDER_PATH + r'\*.txt'


def HandleSample(voutIndexToVal):
    peaks, _ = signal.find_peaks(voutIndexToVal, height=2.8)
    return peaks.shape[0]


def createCSV():
    filesToRead = glob.glob(FILE_PATH)
    for res in filesToRead:
        print(res)

        with open(res, 'r') as in_file:
            timeVed = []
            spikeVout = []

            iinToFreq = {}
            firstLine = in_file.readline()
            firstLine2 = in_file.readline()
            splittedLine = firstLine2.split()
            iin = SpiceToFloat(splittedLine[2].split("=")[1])

            for line in in_file:
                splittedLine = line.split()

                if 'Step' in line:
                    print(line)

                    freq = HandleSample(spikeVout)
                    iinToFreq[iin] = freq

                    iin = SpiceToFloat(splittedLine[2].split("=")[1])

                    timeVed = []
                    spikeVout = []

                else:
                    splittedLine = [SpiceToFloat(x) for x in splittedLine]
                    timeVed.append(splittedLine[0])
                    spikeVout.append(splittedLine[1])

            print("Done")
            freq = HandleSample(spikeVout)
            iinToFreq[iin] = freq

            cvsFileName = res.replace(".txt", ".csv")

            with open(cvsFileName, mode='w', newline='') as out_file:
                writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                firstLine = ["Iin", "Freq"]
                writer.writerow(firstLine)
                for k in iinToFreq.keys():
                    try:
                        iin = k
                        freq = iinToFreq[iin]
                        writer.writerow([iin, freq])

                    except:
                        print("asdas")


start = time.time()
createCSV()
print("Time: {}".format(time.time() - start))
