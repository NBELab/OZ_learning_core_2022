import ltspice
import glob
import os
from subprocess import Popen, PIPE
import csv

LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

CIRCUIT_FOLDER = r"C:\Users\Avi\Desktop\IntelliSpikesLab\IEEE\FIG1\curvesCircuits"


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

            out_file.write(header+"\n")

            for i in range(l.case_count):
                time = l.get_time(i)
                vin = l.getData('V(vin)', i)[0]

                spikes = []
                for x in range(spikesNumber):
                    t = l.getData('V(spikes{})'.format(x + 1), i)
                    spikes.append(t)

                out_file.write("Step Information: Vin={} (Run: {}/{})\n".format(vin, i + 1, l.case_count))

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
    txtFiles = glob.glob(CIRCUIT_FOLDER + r'\*.txt')
    for res in txtFiles:
        print("Converting {} to CSV".format(res))

        with open(res, 'r') as in_file:
            firstLine = in_file.readline().replace("\t", " ").replace("\n", " ").strip()
            NumberOfOutputs = len(firstLine.split()) - 1

            timeVed = []
            voutIndexToVal = {}
            vin = None

            vinValToVoutMap = {}

            for x in range(1, NumberOfOutputs + 1):
                voutIndexToVal[x] = []

            for line in in_file:
                splittedLine = line.split()

                if 'Step' in line:
                    print(line)

                    if vin is None:
                        vin = toFloat(splittedLine[2].split("=")[1])

                    if len(timeVed) != 0:
                        freqMap = HandleSample(voutIndexToVal)
                        vinValToVoutMap[vin] = freqMap

                        try:
                            vin = toFloat(splittedLine[2].split("=")[1])
                        except:
                            print("ccc")

                        timeVed.clear()
                        for x in range(1, NumberOfOutputs + 1):
                            voutIndexToVal[x] = []

                    continue

                splittedLine = [toFloat(x) for x in splittedLine]
                timeVed.append(splittedLine[0])

                for x in range(1, NumberOfOutputs + 1):
                    l = voutIndexToVal[x]
                    l.append(splittedLine[x])
                    voutIndexToVal[x] = l

            print("Done")
            freqMap = HandleSample(voutIndexToVal)
            vinValToVoutMap[vin] = freqMap

            cvsFileName = res.replace(".txt", ".csv")

            with open(cvsFileName, mode='w', newline='') as out_file:
                writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                firstLine = firstLine.split()
                writer.writerow(firstLine)
                for k in vinValToVoutMap.keys():
                    try:
                        vin = k
                        freq = list(vinValToVoutMap[k].values())
                        freq = [vin] + freq

                        writer.writerow(freq)

                    except:
                        print("asdas")


# RunSim()
ConvertRAWtoTXT()
ConvertTXTtoCSV()
