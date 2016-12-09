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
        t = t + ((0.0,) * (size - l))
    return t

def PrepareTrainingSet(units, trainingSet):

    if not all(isinstance(e, TrainingSet) for e in trainingSet):
        raise Exception("Training set element has invalid type!")

    prepared = []
    for training in trainingSet:
        netIn = FixTupleSize(training.input, units)
        netOut = FixTupleSize(training.output, units)
        prepared.append(TrainingSet(training.operation, netIn, netOut))
    return prepared

class NeuralNet:

    def __init__(self, layers, units, encoding=None):
        self.layers = layers
        self.units = units

        if encoding is None:
            self.CreateRandomConnections()
            self.CreateRandomBias()
        else:
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


    def Train(self, cycles, trainingSet, learningRate):

        for i in range(cycles):
            totalError = 0.0
            for training in trainingSet:
                self.FeedForward(training.input)
                totalError += self.Backpropagate(training.output, learningRate)
            self.lastError = totalError / len(trainingSet)

    def GetError(self):
        if not hasattr(self, 'lastError'):
            raise Exception("Must backpropagate before error can be given")
        return self.lastError

    def GetResults(self, trainingSet):

        results = []
        for training in trainingSet:
            out = "%-5s: " % training.operation
            for input in training.input:
                out += "%.2f " % input
            out += "-> "
            for output in self.FeedForward(training.input):
                out += "%.2f " % output
            results.append(out)
        return results

if __name__ == "__main__":
    trainingSet = []
    trainingSet.append(TrainingSet(operation="xor", input=(0.0, 0.0), output=(0.0,)))
    trainingSet.append(TrainingSet(operation="xor", input=(0.0, 1.0), output=(1.0,)))
    trainingSet.append(TrainingSet(operation="xor", input=(1.0, 0.0), output=(1.0,)))
    trainingSet.append(TrainingSet(operation="xor", input=(1.0, 1.0), output=(0.0,)))

    nn = NeuralNet(6, 2)
    nn.Train(trainingSet, 1000, 3.0, lambda r: r * 0.98, 1000)
    print nn.GetResults(trainingSet)


    #nn.Train(trainingSet, 100000, 1.0, lambda rate: rate * 0.98, 1000)
    #nn.PrintResults(trainingSet)
