#!/bin/python2.7

import numpy as np
import numpy.random as npRandom
import collections
import struct

from math import exp

TrainingSet = collections.namedtuple('TrainingSet', 'operation input output')

def Activation(value):
    return 1 / (1 + exp(-value))

def ActivationDerivation(value):
    act = Activation(value)
    return act * (1 - act)

def FixTupleSize(t, size):
    l = len(t)
    if l > size:
        t = t[:size]
    elif l < size:
        t = t + (0,) * (size - l)
    return t

class NeuralNet:

    def __init__(self, layers, units, encoding=None):
        self.layers = layers
        self.units = units

        if encoding is None:
            print 'Create Random'
            self.CreateRandomConnections()
            self.CreateRandomBias()
        else:
            print 'Create by Encoding'
            self.CreateConnections()
            self.CreateBias()
            self.Decode(encoding)

    def GetDimensions(self):
        return (self.layers, self.units)

    def GetBias(self, layer, unit):
        return self.bias[layer][unit]

    def GetConnection(self, layer, srcUnit, destUnit):
        return self.connections[layer][srcUnit][destUnit]

    def CreateRandomConnections(self):
        self.connections = -1.0 + 2.0 * npRandom.rand(self.layers, self.units, self.units)

    def CreateRandomBias(self):
        self.bias = -1.0 + 2.0 * npRandom.rand(self.layers, self.units)

    def CreateConnections(self):
        self.connections = np.zeros((self.layers, self.units, self.units))

    def CreateBias(self):
        self.bias = np.zeros((self.layers, self.units))

    def Encode(self):
        encoding = ''
        iter = np.nditer(self.connections[0:,:,0], flags=["multi_index"])
        while not iter.finished:
            layer = iter.multi_index[0]
            node = iter.multi_index[1]
            encoding += struct.pack("<d%ud" % self.units, self.bias[layer][node], *self.connections[layer][node])
            #print self.bias[layer][node], self.connections[layer][node]

            iter.iternext()
        return encoding

    def Decode(self, encoding):
        iter = np.nditer(self.connections[:,:,0], flags=["multi_index"])
        fmt = "<d%ud" % self.units

        size = struct.calcsize(fmt)
        pos = 0
        while not iter.finished:
            layer = iter.multi_index[0]
            node = iter.multi_index[1]

            data = struct.unpack_from(fmt, encoding, pos)

            self.bias[layer][node] = data[0]
            self.connections[layer][node] = data[1:]
            #print self.bias[layer][node], self.connections[layer][node]

            pos += size
            iter.iternext()

    def FeedForward(self, input):
        self.inputs = np.zeros(self.connections.shape[:2], dtype=self.connections.dtype)
        self.outputs = np.zeros_like(self.inputs)

        self.inputs[0] = input
        self.outputs[0] = input

        for layer in range(0, self.layers - 1):
            for unit in range(self.units):
                if layer > 0:
                    self.outputs[layer][unit] = Activation(self.bias[layer][unit] + self.inputs[layer][unit])
                for conn in range(self.units):
                    self.inputs[layer + 1][conn] += self.outputs[layer][unit] * self.connections[layer][unit][conn]

        for unit in range(self.units):
            self.outputs[-1][unit] = Activation(self.inputs[-1][unit])


        #iter = np.nditer(self.connections[1:,:,0], flags=["multi_index"])
        #while not iter.finished:
        #    layer = 1 + iter.multi_index[0]
        #    node = iter.multi_index[1]
        #    self.inputs[layer][node] = self.bias[layer][node] + sum(self.outputs[layer - 1] * self.connections[layer][node])
        #    self.outputs[layer][node] = Activation(self.inputs[layer][node])

        #    iter.iternext()

        return self.outputs[-1]

    def Backpropagate(self, target, learnRate):
        if not hasattr(self, 'inputs') or not hasattr(self, 'outputs'):
            raise Exception("Must Feed forward before backpropagation!")

        deltas = np.zeros_like(self.outputs)

        for unit in range(self.units):
            deltas[-1][unit] = ActivationDerivation(self.inputs[-1][unit]) * (target[unit] - self.outputs[-1][unit])

        for layer in range(self.layers - 2, -1, -1):
            for unit in range(self.units):
                o = self.outputs[layer][unit]
                i = self.inputs[layer][unit]
                prevDeltas = deltas[layer + 1]
                conn = self.connections[layer][unit]
                deltas[layer][unit] = ActivationDerivation(i) * sum(prevDeltas * conn)


        for layer in range(self.layers - 1):
            for unit in range(self.units):
                for conn in range(self.units):

                    change = learnRate * deltas[layer + 1][conn] * self.outputs[layer][unit]
                    #if change / self.connections[layer][unit][conn] > 0.1 :
                    #    print "%d/%d -> %d/%d: %.2f%%" % (layer, unit, layer+1, conn, change * 100)
                    self.connections[layer][unit][conn] += change


        squareError = 0.5 * sum(((target - self.outputs[-1])**2))

        return squareError

    def PrepareTrainingSet(self, trainingSet):

        if not all(isinstance(e, TrainingSet) for e in trainingSet):
            raise Exception("Training set element has invalid type!")

        prepared = []
        for training in trainingSet:
            netIn = FixTupleSize(training.input, self.units)
            netOut = FixTupleSize(training.output, self.units)
            prepared.append(TrainingSet(training.operation, netIn, netOut))
        return prepared


    def Train(self, trainingSet, runs, initialLearningRate, learningChange, changeFrequency):

        trainingSet = self.PrepareTrainingSet(trainingSet)

        learningRate = initialLearningRate
        for i in range(1, runs + 1):
            totalError = 0.0
            for training in trainingSet:
                self.FeedForward(training.input)
                totalError += self.Backpropagate(training.output, learningRate)

            #self.PrintResults(trainingSet)

            if i % changeFrequency == 0:
                learningRate = learningChange(learningRate)

            if i % 1000 == 0:
                print "run: %6d, learning rate: %.4f, error: %.6f" % (i, learningRate, totalError)
                #self.PrintResults(trainingSet)

    def PrintResults(self, trainingSet):
        for training in trainingSet:
            print training.operation, ": ",
            for input in training.input:
                print "%.2f " % input,
            print "-> ",
            for output in self.FeedForward(training.input):
                print "%.2f " % output,
            print

if __name__ == "__main__":
    trainingSet = []
    trainingSet.append(TrainingSet(operation="or", input=(0.0, 0.0), output=(0.0,)))
    trainingSet.append(TrainingSet(operation="or", input=(0.0, 1.0), output=(1.0,)))
    trainingSet.append(TrainingSet(operation="or", input=(1.0, 0.0), output=(1.0,)))
    trainingSet.append(TrainingSet(operation="or", input=(1.0, 1.0), output=(1.0,)))

    nn = NeuralNet(4, 2)
    nn.Train(trainingSet, 10000, 1.0, lambda r: r * 1.0, 1000)
    nn.PrintResults(trainingSet)


    #nn.Train(trainingSet, 100000, 1.0, lambda rate: rate * 0.98, 1000)
    #nn.PrintResults(trainingSet)
