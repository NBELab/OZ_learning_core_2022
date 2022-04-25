import csv
import glob

import pandas

from NeuralEmulator.Utils.Utils import SpiceToFloat

FOLDER_PATH = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\PulseFull"
FILE_PATH = FOLDER_PATH + r'\*.txt'

filesToRead = glob.glob(FILE_PATH)
for res in filesToRead:
    print(res)

    with open(res, 'r') as in_file:
        timeVed = []
        spikeVout = []

        iinToFreq = {}
        firstLine = in_file.readline()

        label = firstLine.split()[1]
        label = "IOUT"

        firstLine2 = in_file.readline()
        splittedLine = firstLine2.split()
        splittedLine = splittedLine[2:-2]

        cols = []
        vals = []
        for c in splittedLine:
            c = c.split("=")
            cols.append(c[0])
            vals.append(SpiceToFloat(c[1]))

        data = {label: []}

        for x in cols:
            data[x] = []

        for line in in_file:
            splittedLine = line.split()

            if 'Step' in line:
                print(line)
                splittedLine = splittedLine[2:-2]

                vals = []
                for c in splittedLine:
                    c = c.split("=")
                    vals.append(SpiceToFloat(c[1]))


            else:
                try:
                    splittedLine = [SpiceToFloat(x) for x in splittedLine]

                    if cols[0] not in data[cols[0]]:
                        data[cols[0]].append(vals[0])
                        data[cols[1]].append(vals[1])
                        data[label].append(splittedLine[-1])
                except:
                    print("asd")


    df = pandas.DataFrame.from_dict(data)
    df = df.drop_duplicates()
    cvsFileName = res.replace(".txt", ".csv")
    df.to_csv(cvsFileName,index=False)
