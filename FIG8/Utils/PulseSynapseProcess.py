import pandas as pd
import csv
import sys, traceback

FILE_PATH = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\pulseSynapse\PulseSynapse.txt"
FILE_PATH = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\Ilk\OZ_8_pos_curves.txt"
def toFloat(val):
    if 'm' in val:
        val = val.replace("m", "")
        val = float(val)
        val = val * float(10 ** (-3))
        return val
    if 'µ' in val:
        val = val.replace("µ", "")
        val = float(val)
        val = val * float(10 ** (-6))
        return val
    if 'n' in val:
        val = val.replace("n", "")
        val = float(val)
        val = val * float(10 ** (-9))
        return val

    val = float(val)
    return val


with open(FILE_PATH, 'r') as in_file:
    fl = in_file.readline()
    vin = {}
    preVin = None
    for line in in_file:
        line = line.split()

        if "Step" in line:
            preVin = toFloat(line[2].split("=")[1])
        else:
            try:
                vin[preVin] = toFloat(line[1])
            except:
                print(line)
                vin[preVin] = toFloat(line[1])


    cvsFileName = FILE_PATH.replace(".txt", "_txt.csv")
    with open(cvsFileName, mode='w', newline='') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vin", 'iout'])

        for k in vin.keys():
            writer.writerow([k, vin[k]])


