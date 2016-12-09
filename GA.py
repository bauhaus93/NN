#!/bin/python2.7

import collections
import random

import NN

class Genetic:

    def __init__(self, populationFactory, fitnessFunction, trainingFunction, populationSize, mutationChance, mutationSize):
        self.populationFactory = populationFactory
        self.fitnessFunction = fitnessFunction
        self.trainingFunction = trainingFunction
        self.populationSize = populationSize
        self.mutationChance = mutationChance
        self.mutationSize = mutationSize
        self.population = []

        for i in range(self.populationSize):
            self.population.append(self.populationFactory())

    def NextGeneration(self):
        parentA, parentB = self.Select()

        child = self.Crossover(parentA,parentB)
        if random.random() < self.mutationChance:
            child = self.Mutate(child)

        self.population.append(child)

        [self.trainingFunction(i) for i in self.population]
        self.population.sort(key=Fitness, reverse=True)
        self.population = self.population[:self.populationSize]
        for i in self.population:
            print i.GetError()

    def Select(self):
        return self.population[0], self.population[1]

    def Crossover(self, parentA, parentB):
        return parentA

    def Mutate(self, individual):
        return individual



def Fitness(nn):
    return nn.GetError()

def Training(nn, trainingSet, learningRate):
    nn.Train(100, trainingSet, learningRate)



trainingSet = NN.PrepareTrainingSet(3, [ NN.TrainingSet(operation="xor", input=(0.0, 0.0), output=(0.0,)),
                NN.TrainingSet(operation="xor", input=(0.0, 1.0), output=(1.0,)),
                NN.TrainingSet(operation="xor", input=(1.0, 0.0), output=(1.0,)),
                NN.TrainingSet(operation="xor", input=(1.0, 1.0), output=(0.0,))])

print trainingSet

g = Genetic(lambda: NN.NeuralNet(4, 3),
            lambda nn: Fitness(nn),
            lambda nn: Training(nn, trainingSet, 1.0),
            20,
            0.05,
            0.1)

for i in range(100):
    g.NextGeneration()














