import random
import sys
import time
from concurrent.futures.thread import ThreadPoolExecutor

from NeuralEmulator.AdaptationBlock import AdaptationBlock
from NeuralEmulator.ClusterSources import ClusterCurrentSource
from NeuralEmulator.Configurators.NormalLeakSourceConfigurator import NormalLeakSourceConfigurator
from NeuralEmulator.Configurators.OZNeuronConfigurator import OZNeuronConfigurator
from NeuralEmulator.Configurators.PulseSynapseVWConfigurator import PulseSynapseVWConfigurator
from NeuralEmulator.Configurators.STDPSynapseConfigurator import STDPSynapseConfigurator
from NeuralEmulator.Configurators.TemporalConfigurator import TemporalConfigurator
from NeuralEmulator.ErrorBlock import ErrorBlock
from NeuralEmulator.LearningBlock import LearningBlock
from NeuralEmulator.NormalLeakSource import NormalLeakSource
from NeuralEmulator.OZNeuron import OZNeuron
from NeuralEmulator.Preprocessing.NegPreprocessingBlock import NegPreprocessingBlock
from NeuralEmulator.Preprocessing.PosPreprocessingBlock import PosPreprocessingBlock
from NeuralEmulator.Preprocessing.PreprocessingBlock import PreprocessingBlockPos
from NeuralEmulator.PulseSynapse import PulseSynapseWeighted
from NeuralEmulator.STDPSynapse import STDPSynapse
from NeuralEmulator.TemporalIntegration import TemporalIntegration
from NeuralEmulator.Utils.Utils import getObjID
from NeuralEmulator.VoltageSources.LinearSignal import StaticSource
from NeuralEmulator.Adder import Adder
import pandas as pd
import matplotlib.pyplot as plt


def runObj(obj):
    obj.run()


def loadSources():
    file_path = r"C:\Users\Avi\Desktop\IntelliSpikesLab\MultiLayer\DataSet\IRIS_P1.csv"
    df = pd.read_csv(file_path)

    X = df[["sepal_length", "sepal_width", "petal_length", "petal_width"]].values
    y = df[["species_Iris-setosa", "species_Iris-versicolor", "species_Iris-virginica"]].values

    v1 = X[:, 0]
    v2 = X[:, 1]
    v3 = X[:, 2]
    v4 = X[:, 3]

    y1 = y[:, 0]
    y2 = y[:, 1]
    y3 = y[:, 2]

    return v1, v2, v3, v4, y1, y2, y3


def buildL2L3(sources, leakesVals):
    pulseSynapseVWConfigurator = PulseSynapseVWConfigurator()
    noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
    ozNeuronConfigurator = OZNeuronConfigurator()

    NEURONS_PER_SOURCE = 4

    L2 = []
    L3 = []
    L4 = []

    staticVWSource = StaticSource(2.4)

    srcids = [getObjID(src) for src in sources]
    print("buildL2L3 sources {}".format(srcids))

    sourcest = sources + []

    while len(sourcest) != 0:
        stdpList = sourcest[0:2]
        del sourcest[0:2]

        for src in stdpList:
            posIndex = 0
            for x in range(int(NEURONS_PER_SOURCE / 2)):
                # Synapses
                positivePulseSynapse = PulseSynapseWeighted(src, staticVWSource, pulseSynapseVWConfigurator)
                # Leak current
                VLK1_CONFIG = np.random.normal(leakesVals[posIndex][x], 0.25, 1)[-1]
                staticLeakSource = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource(VLK1_CONFIG * (10 ** -3)))

                # OZ neuron
                ozNeuron = OZNeuron(ozNeuronConfigurator, positivePulseSynapse, staticLeakSource, invertOutput=True, printLog=True)

                L2.append(positivePulseSynapse)
                L3.append(staticLeakSource)
                L4.append(ozNeuron)

    return L2, L3, L4


def buildSTDPLayer(preNeuronsArr):
    sTDPSynapseConfigurator = STDPSynapseConfigurator()
    preNeuronsArrTemp = preNeuronsArr + []

    preNeuronInChunks = []
    while len(preNeuronsArrTemp) != 0:
        sliceArr = preNeuronsArrTemp[0:4]
        del preNeuronsArrTemp[0:4]
        preNeuronInChunks.append(sliceArr)

    randomEnsambels = set()
    while len(randomEnsambels) != 8:
        i = random.randint(0, 3)
        j = random.randint(0, 3)
        if i == j:
            continue
        t = (i, j)
        randomEnsambels.add(t)

    STDPLayer = []

    while len(randomEnsambels) != 0:
        item = randomEnsambels.pop()
        for neuron in preNeuronInChunks[item[0]]:
            sTDPSynapse = STDPSynapse(sTDPSynapseConfigurator, preSource=neuron,printLog=True)
            STDPLayer.append(sTDPSynapse)

        for neuron in preNeuronInChunks[item[1]]:
            sTDPSynapse = STDPSynapse(sTDPSynapseConfigurator, preSource=neuron,printLog=True)
            STDPLayer.append(sTDPSynapse)

    return STDPLayer


def buildL6(neuronLeakConfig, L5_STDPLayer, L4_neurons):
    print("-I- buildL6(neuronLeakConfig, L5_STDPLayer, L4_neurons)")
    L5_STDPLayerT = L5_STDPLayer + []
    preNeurons = L4_neurons + []

    ozNeuronConfigurator = OZNeuronConfigurator()
    noramalLeakSourceConfigurator = NormalLeakSourceConfigurator()
    temporalConfigurator = TemporalConfigurator()
    pulseSynapseVWConfigurator = PulseSynapseVWConfigurator()

    neurons = []
    synapses = []
    clusterIinSources = []

    NEURON_COUNT = 8

    print("Setting OZ neuron current source")

    for x in range(NEURON_COUNT):

        ozNeuron = OZNeuron(ozNeuronConfigurator)

        stdpList = L5_STDPLayerT[0:8]
        del L5_STDPLayerT[0:8]

        stdpSynapses = []

        for stdpSourceIndex in range(len(stdpList)):
            positivePulseSynapse = PulseSynapseWeighted(preNeurons[stdpSourceIndex], stdpList[stdpSourceIndex], pulseSynapseVWConfigurator, True)
            stdpSynapses.append(positivePulseSynapse)
            stdpList[stdpSourceIndex].setPostSource(ozNeuron)

        clusterCurrentSource = ClusterCurrentSource(stdpSynapses, True)
        ozNeuron.setSynapse(clusterCurrentSource)

        neurons.append(ozNeuron)
        clusterIinSources.append(clusterCurrentSource)

        synapses += stdpSynapses

    print("Setting OZ Leaks")

    leakSources = []
    adaptationList = []

    for x in range(NEURON_COUNT):
        adaptationBlock = AdaptationBlock(temporalConfigurator, neurons[x])
        adaptationIout = NormalLeakSource(noramalLeakSourceConfigurator, adaptationBlock)

        adaptationList.append(adaptationBlock)
        leakSources.append(adaptationIout)

    # Neighbors leak
    clusterIoutSources = []

    for x in range(NEURON_COUNT):
        leakSource0 = NormalLeakSource(noramalLeakSourceConfigurator, StaticSource(neuronLeakConfig))
        leakSource1 = NormalLeakSource(noramalLeakSourceConfigurator, adaptationList[((x - 1) % 7)])
        leakSource2 = NormalLeakSource(noramalLeakSourceConfigurator, adaptationList[((x + 1) % 7)])
        leakSource3 = NormalLeakSource(noramalLeakSourceConfigurator, adaptationList[((x + 3) % 7)])

        ltemp = [leakSource0, leakSource1, leakSource2, leakSource3]

        clusterCurrentSource = ClusterCurrentSource(ltemp)

        neurons[x].setLeakSource(clusterCurrentSource)
        leakSources += ltemp
        clusterIoutSources.append(clusterCurrentSource)

    return clusterIoutSources, adaptationList, leakSources, synapses, clusterIinSources, neurons


def buildL11(temporalConfig, neuronsList):
    temporalConfigurator = TemporalConfigurator()
    temporals = []
    for n in neuronsList:
        temporalIntegration = TemporalIntegration(temporalConfig, temporalConfigurator, n)
        temporals.append(temporalIntegration)
    return temporals


def buildL12(neuronsTemporals):
    LR = 0.01

    learningBlocks = []
    for x in range(3):
        for neuronTempSignal in neuronsTemporals:
            learningBlock1 = LearningBlock(LR, neuronTempSignal)
            learningBlocks.append(learningBlock1)

    return learningBlocks


def buildAdders(learningBlocks):
    adders = []
    learningBlockst = learningBlocks + []
    for x in range(3):
        learningUnits = learningBlockst[0:8]
        del learningBlockst[0:8]
        ade = Adder(learningUnits)
        adders.append(ade)
    return adders


def buildErrorCkt(adders, sources):
    errorBlocks = []
    for x in range(len(adders)):
        errorBlock = ErrorBlock(adders[x], sources[x], 8)
        errorBlocks.append(errorBlock)
    return errorBlocks


def connectLearningBlockWithError(lrb, errl):
    learningBlockst = lrb + []

    for x in range(4):
        learningUnits = learningBlockst[0:8]
        del learningBlockst[0:8]
        for lu in learningUnits:
            lu.setErrorBlock(errl[x])


def setSTDPPostSignals(STDPLayer, postNeurons):
    L5_STDPLayerT = STDPLayer + []

    for neuron in postNeurons:
        learningUnits = L5_STDPLayerT[0:8]
        del L5_STDPLayerT[0:8]
        for stdp in learningUnits:
            stdp.setPostSource(neuron)


def resetLayer(layer):
    for l in layer:
        l.reset()


L1_NEURON_COUNT = 4

if __name__ == "__main__":
    import numpy as np
    import os

    os.environ["NERUSIM_CONF"] = r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\config"

    sTDPSynapseConfigurator = STDPSynapseConfigurator()

    steps = int(1.0 // sTDPSynapseConfigurator.getStepTime())

    # Sources
    v1ValList, v2ValList, v3SValList, v4ValList, y1ValList, y2ValList, y3ValList = loadSources()

    v1Source = StaticSource(0)
    v2Source = StaticSource(1)
    v3Source = StaticSource(2)
    v4Source = StaticSource(3)

    y1Source = StaticSource(4)
    y2Source = StaticSource(5)
    y3Source = StaticSource(6)

    L1_Sources = [v1Source, v2Source, v3Source, v4Source, y1Source, y2Source, y3Source]

    # Preprocessing blocks

    v1PrerocessingBlock = PreprocessingBlockPos(v1Source)
    v2PrerocessingBlock = PreprocessingBlockPos(v2Source)
    v3PrerocessingBlock = PreprocessingBlockPos(v3Source)
    v4PrerocessingBlock = PreprocessingBlockPos(v4Source)

    L1_PrerocessingBlocks = [v1PrerocessingBlock, v2PrerocessingBlock, v3PrerocessingBlock, v4PrerocessingBlock]

    vposPort1 = PosPreprocessingBlock(v1PrerocessingBlock)
    vnegPort1 = NegPreprocessingBlock(v1PrerocessingBlock)

    vposPort2 = PosPreprocessingBlock(v2PrerocessingBlock)
    vnegPort2 = NegPreprocessingBlock(v2PrerocessingBlock)

    vposPort3 = PosPreprocessingBlock(v3PrerocessingBlock)
    vnegPort3 = NegPreprocessingBlock(v3PrerocessingBlock)

    vposPort4 = PosPreprocessingBlock(v4PrerocessingBlock)
    vnegPort4 = NegPreprocessingBlock(v4PrerocessingBlock)

    L1_PrerocessingBlocksPorts = [vposPort1, vnegPort1, vposPort2, vnegPort2, vposPort3, vnegPort3, vposPort4, vnegPort4]

    # L2/3/4
    leakesValsPos = [720.0, 700.0]
    leakesValsNeg = [675.0, 650.0]

    L2_synapses, L3_leakes, L4_neurons = buildL2L3(L1_PrerocessingBlocksPorts, (leakesValsPos, leakesValsNeg))

    # L5
    L5_STDPLayer = buildSTDPLayer(L4_neurons)

    # L6-10
    clusterIoutSources, adaptationList, leakSources, synapses, clusterIinSources, neurons = buildL6(745.0 * (10 ** -3), L5_STDPLayer, L4_neurons)

    # L11
    temporals = buildL11(450 * (10 ** -3), neurons)

    # L12
    learningBlocks = buildL12(temporals)

    # L13
    adders = buildAdders(learningBlocks)

    # L14
    errorCkts = buildErrorCkt(adders, L1_Sources[4:])

    # Connect LearningBlock with Error signal
    connectLearningBlockWithError(learningBlocks, errorCkts)

    layers = [L1_Sources, L1_PrerocessingBlocks, L1_PrerocessingBlocksPorts,
              L2_synapses, L3_leakes, L4_neurons,
              L5_STDPLayer, clusterIoutSources, adaptationList, leakSources, synapses, clusterIinSources, neurons,
              temporals, learningBlocks, adders, errorCkts]

    layers = [L1_Sources, L1_PrerocessingBlocks, L1_PrerocessingBlocksPorts,
              L2_synapses, L3_leakes, L4_neurons, L5_STDPLayer,clusterIoutSources, adaptationList, leakSources, synapses, clusterIinSources, neurons
              ]

    numberOfTrainSamples = int(len(v1ValList) * 0.7)
    numberOfTestingSamples = len(v1ValList) - numberOfTrainSamples

    epochs = 10

    SampleTrainTime = 150 * (10 ** -3)
    trainTime = SampleTrainTime * numberOfTrainSamples

    trainStepsCount = int((SampleTrainTime / sTDPSynapseConfigurator.getStepTime()) + 0.5)
    testStepsCount = int(((SampleTrainTime / 2) / sTDPSynapseConfigurator.getStepTime()) + 0.5)

    print("-I- Start training")

    for epoch in range(epochs):

        startTime = time.time()
        tableRowIndex = 0

        for st in L5_STDPLayer:
            st.setLearningVal(True)

        for lrb in learningBlocks:
            lrb.setLearningVal(True)

        xvals = []
        yvals = [[] for x in L4_neurons]

        for trainSampleStep in range(numberOfTrainSamples):
            sys.stdout.write("\rSample {}/{}".format(trainSampleStep, numberOfTrainSamples))
            # print("\rSample {}/{}".format(trainSampleStep, numberOfTrainSamples))
            v1Source.setVoltage(v1ValList[trainSampleStep])
            v2Source.setVoltage(v2ValList[trainSampleStep])
            v3Source.setVoltage(v3SValList[trainSampleStep])
            v4Source.setVoltage(v4ValList[trainSampleStep])

            y1Source.setVoltage(y1ValList[trainSampleStep])
            y2Source.setVoltage(y2ValList[trainSampleStep])
            y3Source.setVoltage(y3ValList[trainSampleStep])

            resetLayer(L4_neurons)
            resetLayer(neurons)
            resetLayer(temporals)
            resetLayer(L5_STDPLayer)


            xvals = []
            preNeurons = [[] for x in L4_neurons]
            stdpWeights = [[] for x in L5_STDPLayer]
            postNeurons = [[] for x in neurons]
            temporalVals = [[] for x in temporals]
            PESWights = [[] for x in learningBlocks]

            for step in range(trainStepsCount):
                xvals.append(step)
                for layer in layers:
                    for obj in layer:
                        obj.run()

                for x in range(len(L4_neurons)):
                    preNeurons[x].append(L4_neurons[x].getVoltage())

                for x in range(len(L5_STDPLayer)):
                    stdpWeights[x].append(L5_STDPLayer[x].getVoltage())

                for x in range(len(neurons)):
                    postNeurons[x].append(neurons[x].getVoltage())

                for x in range(len(temporals)):
                    temporalVals[x].append(temporals[x].getVoltage())

                for x in range(len(learningBlocks)):
                    PESWights[x].append(learningBlocks[x].getVoltage())

            fig, axs = plt.subplots(16, 3)
            x = 0
            for y in preNeurons:
                axs[x, 0].plot(xvals, y)
                x += 1

            x = 0
            for y in postNeurons:
                axs[x, 1].plot(xvals, y)
                x += 1

            # x = 0
            # for y in temporalVals:
            #     axs[x, 2].plot(xvals, y)
            #     x += 1
            #
            # x = 0
            # for y in PESWights:
            #     axs[x, 3].plot(xvals, y)
            #     x += 1

            plt.show()
        #
        # for st in L5_STDPLayer:
        #     st.setLearningVal(False)
        #
        # for lrb in learningBlocks:
        #     lrb.setLearningVal(False)
        #
        # trainCorrectCount = 0
        #
        # for trainSampleStep in range(numberOfTrainSamples):
        #
        #     v1Source.setVoltage(v1ValList[trainSampleStep])
        #     v2Source.setVoltage(v2ValList[trainSampleStep])
        #     v3Source.setVoltage(v3SValList[trainSampleStep])
        #     v4Source.setVoltage(v4ValList[trainSampleStep])
        #
        #     y1Source.setVoltage(y1ValList[trainSampleStep])
        #     y2Source.setVoltage(y2ValList[trainSampleStep])
        #     y3Source.setVoltage(y3ValList[trainSampleStep])
        #
        #     for step in range(trainStepsCount):
        #         for layer in layers:
        #             for obj in layer:
        #                 obj.run()
        #
        #     predicts = [adders[0].getVoltage(), adders[1].getVoltage(), adders[2].getVoltage()]
        #     labels = [y1Source.getVoltage(), y2Source.getVoltage(), y3Source.getVoltage()]
        #     print("Predict {}".format(predicts))
        #     print("True {}".format(labels))
        #
        #     if predicts.index(max(predicts)) == labels.index(max(labels)) and max(predicts) != 0:
        #         trainCorrectCount += 1

        # print("Train accuracy {}".format((trainCorrectCount / numberOfTrainSamples) * 100.0))
        print("\nEpoch Simulation runtime {}".format(time.time() - startTime))

    # # ------- Testing ------------------
    #
    # testSamplesCounter = 0
    # currectCounter = 0
    #
    # tableRowIndex = numberOfTrainSamples
    #
    # for st in L5_STDPLayer:
    #     st.setLearningVal(False)
    #
    # for lrb in learningBlocks:
    #     lrb.setLearningVal(False)
    #
    # for testSampleStep in range(numberOfTestingSamples):
    #
    #     v1Source.setVoltage(v1ValList[tableRowIndex])
    #     v2Source.setVoltage(v2ValList[tableRowIndex])
    #     v3Source.setVoltage(v3SValList[tableRowIndex])
    #     v4Source.setVoltage(v4ValList[tableRowIndex])
    #
    #     y1Source.setVoltage(y1ValList[tableRowIndex])
    #     y2Source.setVoltage(y2ValList[tableRowIndex])
    #     y3Source.setVoltage(y3ValList[tableRowIndex])
    #
    #     for step in range(testStepsCount):
    #         for layer in layers:
    #             for obj in layer:
    #                 obj.run()
    #
    #     predicts = [adders[0].getVoltage(), adders[1].getVoltage(), adders[2].getVoltage()]
    #     labels = [y1Source.getVoltage(), y2Source.getVoltage(), y3Source.getVoltage()]
    #     print("Test Predict {}".format(predicts))
    #     print("Test Vals {}".format(labels))
    #     tableRowIndex += 1
    #
    #     testSamplesCounter += 1.0
    #     if predicts.index(max(predicts)) == labels.index(max(labels))and max(predicts) !=0:
    #         currectCounter += 1.0
    #
    # print("Test accuracy {}".format((currectCounter / testSamplesCounter) * 100.0))
