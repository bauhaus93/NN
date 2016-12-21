#!/bin/python2.7

import NN


class Trainer:

    def __init__(self, nn, trainingSet, initialLearningRate, learningModification, learnModFrequency, inputCount, outputCount):
        self.nn = nn
        self.trainingSet = NN.PrepareTrainingSet(nn.GetDimensions()[1], trainingSet)
        self.learningRate = float(initialLearningRate)
        self.learningModification = learningModification
        self.learnModFrequency = learnModFrequency
        self.inputCount = inputCount
        self.outputCount = outputCount
        self.cycles = 0
        self.errors = []


    def Work(self, times):
        self.nn.Train(times, self.trainingSet, self.learningRate)
        self.errors.append(self.nn.GetError())
        if len(self.errors) > 100:
            self.errors = self.errors[1:]
        self.cycles += times
        if self.cycles % self.learnModFrequency == 0:   #TODO make better
            self.learningRate = self.learningModification(self.learningRate)

    def GetResults(self):
        return self.nn.GetResults(self.trainingSet, self.inputCount, self.outputCount)

    def GetCycles(self):
        return self.cycles

    def GetLearningRate(self):
        return self.learningRate

    def GetErrors(self):
        return self.errors

    def GetSummary(self):
        error = self.nn.GetError()
        if error < 1e-2:
            error = "%5.3e" % error
        else:
            error = "%5.3f" % error
        summary = "cycles: %6d | learning rate: %5.3f | error: %s" % (self.cycles, self.learningRate, error)

        return summary
