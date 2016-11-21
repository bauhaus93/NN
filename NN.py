#!/bin/python2.7

import numpy as np
import numpy.random as npRandom
import wx

from math import exp

def Activation(value):
    return 1 / (1 + exp(-value))

def ActivationDerivation(value):
    act = Activation(value)
    return act * (1 - act)

class NeuralNet:

    def __init__(self, layers, units):
        self.layers = layers
        self.units = units

        self.CreateConnections()
        self.CreateBias()

    def GetDimensions(self):
        return (self.layers, self.units)

    def GetBias(self, layer, unit):
        return self.bias[layer][unit]

    def GetConnection(self, layer, srcUnit, destUnit):
        return self.connections[layer][srcUnit][destUnit]

    def CreateConnections(self):
        self.connections = -10 + 20 * npRandom.rand(self.layers, self.units, self.units)

    def CreateBias(self):
        self.bias = -10 + 20 * npRandom.rand(self.layers, self.units)

    def FeedForward(self, input):
        self.inputs = np.zeros(self.connections.shape[:2], dtype=self.connections.dtype)
        self.outputs = np.zeros_like(self.inputs)

        self.inputs[0] = input
        self.outputs[0] = input

        iter = np.nditer(self.connections[1:,:,0], flags=["multi_index"])
        while not iter.finished:
            layer = 1 + iter.multi_index[0]
            node = iter.multi_index[1]
            self.inputs[layer][node] = self.bias[layer][node] + sum(self.outputs[layer - 1] * self.connections[layer][node])
            self.outputs[layer][node] = Activation(self.inputs[layer][node])
            iter.iternext()

        return self.outputs[-1]

    def Backpropagate(self, target, learnRate=0.2):
        if not hasattr(self, 'inputs') or not hasattr(self, 'outputs'):
            return
        totalSquare = 0.5 * sum((target - self.outputs[-1])**2)
        print totalSquare
        deltas = np.zeros_like(self.inputs)

        iter = np.nditer(self.inputs[-1], flags=["f_index"])
        while not iter.finished:
            node = iter.index
            deltas[-1][node] = ActivationDerivation(iter[0]) * (target[node] - self.outputs[-1][node])
            iter.iternext()


        iter = np.nditer(self.connections[:-1,:,0], flags=["multi_index"])
        while not iter.finished:
            layer = self.layers - iter.multi_index[0] - 2
            node = iter.multi_index[1]

            deltas[layer][node] = ActivationDerivation(self.inputs[layer][node]) * sum(deltas[layer + 1] * iter[0])
            self.bias[layer][node] += learnRate * deltas[layer][node] * self.outputs[layer][node]
            iter.iternext()

        iter = np.nditer(self.connections, flags=["multi_index"], op_flags=["readwrite"])
        while not iter.finished:
            layer = iter.multi_index[0]
            node = iter.multi_index[1]
            conn = iter.multi_index[2]

            iter[0] += learnRate * deltas[layer][node] * self.outputs[layer][node]

            iter.iternext()



if __name__ == "__main__":
    nn = NeuralNet(4, 4)
    #trainingSet = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)]
    for i in range(10000):
        nn.FeedForward([1]*4)
        nn.Backpropagate([0.1234]*4)
    print map(lambda n: round(n, 2), nn.FeedForward([0.1234]*4))
    #    for train in trainingSet:
    #        output = nn.FeedForward(train[:2])
    #        nn.Backpropagate([train[2], 0], 0.2)

    #for train in trainingSet:
    #    output = nn.FeedForward(train[:2])
    #    print "%d OR %d = %.4f" % (train[0], train[1], output[0])
    #print output
