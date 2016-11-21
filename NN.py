#!/bin/python2.7

import numpy as np
import numpy.random as npRandom
import wx

from math import exp

def Activation(value):
    return 1 / (1 + exp(-value))

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
        values = np.zeros(self.connections.shape[:2], dtype=self.connections.dtype)

        values[0] = input
        iter = np.nditer(self.connections[1:,:,0], flags=["multi_index"])
        while not iter.finished:
            layer = 1 + iter.multi_index[0]
            node = iter.multi_index[1]
            values[layer][node] = Activation(self.bias[layer][node] + sum(values[layer - 1] * self.connections[layer][node]))
            iter.iternext()
        self.values = values

        return values[-1]

    def Backpropagate(self, target):
        if not hasattr(self, 'values'):
            return


if __name__ == "__main__":
    nn = NeuralNet(4, 4)
    output = nn.FeedForward([1]*4)
    nn.Backpropagate([1]*4)
    print output
