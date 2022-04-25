import os
import pandas as pd
from arm import Model, Simulation
import numpy as np
import os
import logging
import time
import mujoco_py as mjc

# os.environ["NERUSIM_CONF"] = "/home/avi/PycharmProjects/mujoco/NeuralEmulator/IntelliSpikesLab/Config"
#
# BASE_DIR = '/home/avi/Projects/Adaptive_arm_control/'
# BASE_DIR = ''
#
#
# class Results:
#     def __init__(self, logFile):
#         self.xVals = []
#         self.yVals = []
#         self.zVals = []
#
#         self.logFile = logFile
#
#         self.logger = logging.getLogger(logFile)
#         self.logger.setLevel(logging.DEBUG)
#         fh = logging.FileHandler(logFile)
#         fh.setLevel(logging.DEBUG)
#         self.logger.addHandler(fh)
#
#     def pushX(self, vals):
#         self.xVals.append(vals)
#
#     def pushY(self, vals):
#         self.yVals.append(vals)
#
#     def pushZ(self, vals):
#         self.zVals.append(vals)
#
#     def write(self):
#         header = ""
#         for target in range(len(self.xVals)):
#             linetag = "x{},y{},z{}".format(target, target, target)
#             header = header + linetag + ","
#
#         header = header[:-1]
#
#         self.logger.info(header)
#
#         for rowIndex in range(len(self.xVals[0])):
#             row = ""
#             for target in range(len(self.xVals)):
#                 try:
#                     xVec = self.xVals[target]
#                     yVec = self.yVals[target]
#                     zVec = self.zVals[target]
#                     rowTag = "{},{},{}".format(xVec[rowIndex], yVec[rowIndex], zVec[rowIndex])
#                     row = row + rowTag + ","
#                 except:
#                     pass
#
#             row = row[:-1]
#
#             self.logger.info(row)
#
#         self.logger = None
#
#
# model_name = 'NBEL'
# model = Model(BASE_DIR + 'arm_models/{}/{}.xml'.format(model_name, model_name))
#
# init_angles = {0: -np.pi / 2, 1: 0, 2: np.pi / 2, 3: 0, 4: np.pi / 2, 5: 0}
#
#
# ozNetwork = False
#
# forces = [2.0, 3.0]
# adaptions = [False, True]
#
#
#
# if ozNetwork is True:
#     adaptions = [True]
#
# targets = [np.array([0.20, 0.10, -0.10]), np.array([-0.20, 0.10, -0.10]),
#            np.array([0.40, 0.050, -0.10]), np.array([-0.40, 0.050, -0.10]),
#            np.array([0.40, 0.025, -0.10]), np.array([-0.40, 0.025, -0.10]),
#            np.array([0.40, 0.010, -0.10]), np.array([-0.40, 0.010, -0.10])
#            ]
#
# simulation = mjc.MjSim(model.mjc_model)
# viewer = mjc.MjViewer(simulation)
# for force in forces:
#     for adapt in adaptions:
#         adaptLabel = "adapt" if adapt else "noAdapt"
#         isOzNetworkLabel = "OzNetwork" if ozNetwork else "Nengo"
#         fileName = "force_{}_{}_{}.csv".format(force, adaptLabel, isOzNetworkLabel)
#
#         if os.path.exists(fileName):
#             os.remove(fileName)
#
#         print("Writing {}".format(fileName))
#
#         results = Results(fileName)
#         target = targets
#         simulation_ext_adapt = Simulation(model, init_angles, external_force=force, target=target, adapt=adapt,
#                                           results=results, simulation=simulation, viewer=viewer)
#         simulation_ext_adapt.simulate(4000)
#         results.write()
#
# print('Done')

import matplotlib.pyplot as plt
fileName = "force_{}_{}_{}.csv".format(3.0, "adapt","OzNetwork")
df = pd.read_csv(fileName)
cols = [x for x in df.columns]

ax = plt.figure().add_subplot(111, projection='3d')

for index in range(0, len(cols), 3):
    labels = cols[index:index + 3]
    print(labels)
    xVals = [float(x) for x in df[labels[0]]]
    yVals = [float(x) for x in df[labels[1]]]
    zVals = [float(x) for x in df[labels[2]]]
    ax.scatter(xVals, yVals, zVals)
plt.show()
