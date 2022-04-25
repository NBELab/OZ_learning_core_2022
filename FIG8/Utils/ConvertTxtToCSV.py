import glob
import csv
import os
import pandas as pd

FOLDER_PATH = r'C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\circuits\Ilk'
FILE_PTRN = r'*.txt'


FILE_PATH = FOLDER_PATH +"\\"+FILE_PTRN
filesToRead = glob.glob(FILE_PATH)

for res in filesToRead:
    print(res)
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

