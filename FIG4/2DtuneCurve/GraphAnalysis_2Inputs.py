import csv
import collections
import glob
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
from subprocess import Popen, PIPE
import ltspice

LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
FOLDER_PATH = r'C:\Users\Avi\Desktop\IEEGIT\TBioCAS2021\FIG4\2DtuneCurve'

FILE_PTRN = r"*.txt"
FILE_PATH = FOLDER_PATH + "\\" + FILE_PTRN


def normVoltage(volt):
    if volt <= -40 or volt >= 40:
        volt = volt / 1000.0
    return volt


def HandleSample(timeVed, valVec):
    peakTime = []
    for x in range(len(valVec)):
        if x - 1 < 0 or x + 1 >= len(valVec):
            continue

        try:
            if valVec[x] > valVec[x - 1] and valVec[x] > valVec[x + 1]:
                peakTime.append(timeVed[x])
        except:
            print("Exception")

    freq = len(peakTime)
    return freq


def RunSim():
    circuits = glob.glob(FOLDER_PATH + r'\*.asc')
    print("-I- Number of circuits {}".format(len(circuits)))

    for ckt in circuits:
        print("-I- Run sim {}".format(ckt))
        process = Popen([LTSPICE_PATH, "-b", "-ascii", "-RUN", ckt], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        print("-I- Done")
        break


filesToRead = glob.glob(FILE_PATH)
filesToRead.sort(reverse=True)


# RunSim()

def ConvertRAWtoTXT():
    rawFiles = glob.glob(FOLDER_PATH + r'\*.raw')
    for raw in rawFiles:
        if ".op" in raw:
            continue

        print("-I- Converting {} to TXT".format(raw))

        txtFile = raw.replace(".raw", ".txt")

        with open(txtFile, mode='w', newline='') as out_file:

            l = ltspice.Ltspice(raw)
            l.parse()

            header = "time VOUT"

            out_file.write(header + "\n")

            for i in range(l.case_count):
                time = l.get_time(i)

                spikes = []

                vin1 = l.getData('V(vin1)', i)
                vin2 = l.getData('V(vin2)', i)

                if "-5" in str(vin1[0]):
                    vin1[0] = 0

                if "-5" in str(vin2[0]):
                    vin2[0] = 0

                out_file.write("Step Information: Vin1={} Vin2={}  (Run: {}/{})\n".format(vin1[0], vin2[0],
                                                                                        i + 1,
                                                                                        l.case_count
                                                                                        ))

                vspike = l.getData('V(SPIKES)', i)

                for index in range(time.shape[0]):
                    row = [time[index], vspike[index]]
                    row = [str(x) for x in row]
                    row = " ".join(row) + "\n"
                    out_file.write(row)


def showGraph():
    for res in filesToRead:
        print(res)
        if "readme" in res:
            continue
        # l = res.split("_")
        # print("VWx1 = {}, VWx2= {} , Vlk = {} , Vref = {}".format(l[3],l[2],l[4],l[5]))
        xlabel = None
        ylabel = None

        with open(res, 'r') as in_file:
            title = in_file.readline()

            timeVed = []
            valVec = []
            voltToFreq = {}

            vw = None
            vlk = None

            for line in in_file:

                splittedLine = line.split()

                if len(splittedLine) > 3:
                    if vw is None:
                        vw = splittedLine[2].split("=")[1]
                        xlabel = splittedLine[2].split("=")[0]
                        vw = vw.replace("m", "")
                        vw = float(vw)
                        vw = normVoltage(vw)

                        vlk = splittedLine[3].split("=")[1]
                        ylabel = splittedLine[3].split("=")[0]

                        vlk = float(vlk)
                        vlk = normVoltage(vlk)

                    if len(timeVed) != 0:
                        freq = HandleSample(timeVed, valVec)
                        voltToFreq[(vw, vlk)] = freq
                        try:
                            vw = splittedLine[2].split("=")[1]
                            vw = vw.replace("m", "")
                            if "f" in vw:
                                vw = "0"

                            vw = float(vw)
                            vw = normVoltage(vw)

                            vlk = splittedLine[3].split("=")[1]
                            vlk = vlk.replace("m", "")
                            if "f" in vlk:
                                vlk = "0"
                            vlk = float(vlk)
                            vlk = normVoltage(vlk)


                        except:
                            print("ccc")

                        timeVed.clear()
                        valVec.clear()
                    continue

                splittedLine = [float(x) for x in splittedLine]

                timeVed.append(splittedLine[0])
                valVec.append(splittedLine[1])

            freq = HandleSample(timeVed, valVec)
            voltToFreq[(vw, vlk)] = freq

            pklFileName = res.replace(".txt", ".pkl")

            X = []
            Y = []
            Z = []

            for k in voltToFreq.keys():
                try:
                    X.append(k[0])
                    Y.append(k[1])
                    Z.append(voltToFreq[k])
                except:
                    print("asdas")

            x = np.asarray(X)
            y = np.asarray(Y)
            z = np.asarray(Z)

            ax = plt.axes(projection='3d')

            ax.set_xlabel('x1')
            ax.set_ylabel('x2')
            ax.set_zlabel('Firing rate (Hz)')

            mappable = plt.cm.ScalarMappable(cmap=plt.cm.viridis)
            mappable.set_array(z)
            surf = ax.plot_trisurf(x, y, z, cmap=plt.get_cmap('YlOrRd_r'), norm=mappable.norm, linewidth=0, antialiased=False)

            plt.show()


ConvertRAWtoTXT()
showGraph()
