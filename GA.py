#!/bin/python2.7

import collections
import random
from bisect import bisect

import NN

class Individual:

    def __init__(self, entity, fitnessFunction):
        self.entity = entity
        self.fitnessFunction = fitnessFunction
        self.age = 0
        self.children = 0

    def __str__(self):
        return "fitness: %3.2e, age: %d, children: %d" % (self.fitnessFunction(self.entity), self.age, self.children)

def CumSum(it):
    total = 0
    for x in it:
        total += x
        yield total

class Genetic:

    def __init__(self, populationFactory, fitnessFunction, trainingFunction, populationSize, mutationChance, mutationSize):
        self.populationFactory = populationFactory
        self.fitnessFunction = fitnessFunction
        self.trainingFunction = trainingFunction
        self.populationSize = populationSize
        self.mutationChance = mutationChance
        self.mutationSize = mutationSize
        self.population = []
        self.generations = 0

        for i in range(self.populationSize):
            self.population.append(Individual(self.populationFactory(None), self.fitnessFunction))

    def NextGeneration(self):
        self.generations += 1
        for i in self.population:
            self.trainingFunction(i.entity)
            i.age +=1

        parentA, parentB = self.Select()

        childDna = self.Crossover(parentA,parentB)
        if random.random() < self.mutationChance:
            childDna = self.Mutate(childDna)

        child = self.populationFactory(childDna)
        self.trainingFunction(child)
        self.population.append(Individual(child, self.fitnessFunction))
        self.population.sort(key=lambda i: self.fitnessFunction(i.entity))
        self.population = self.population[:self.populationSize]

    def GetFittest(self):
        return self.population[0].entity

    def GetGenerations(self):
        return self.generations

    #pref: higher number    -> prefer fitter individuals
    #      negative number  -> prefer unfitter individuals
    #      around zero:     -> all individuals selected more equally
    def Select(self, pref=1.0):
        chances = list(CumSum([e**-pref for e in range(1, self.populationSize+1)]))
        selA = bisect(chances, random.uniform(0, chances[-1]))
        selB = selA
        while selA == selB:
            selB = bisect(chances, random.uniform(0, chances[-1]))

        return self.population[selA], self.population[selB]

    def Crossover(self, parentA, parentB):
        dnaA = parentA.entity.Encode()
        dnaB = parentB.entity.Encode()

        assert len(dnaA) == len(dnaB), "encoding lenghts do not match: %d / %d!" % (len(dnaA), len(dnaB))
        splitPoint = random.randint(0, len(dnaA)-1)

        dnaChild = dnaA[:splitPoint] + dnaB[splitPoint:]
        parentA.children += 1
        parentB.children += 1
        return dnaChild

    def Mutate(self, dna):
        dna = bytearray(dna)
        dnaLen = len(dna)
        for i in range(int(dnaLen*self.mutationSize)):
            r = random.randint(0, dnaLen-1)
            if random.randint(0, 1) == 0:
                if dna[r] == 0xFF:
                    dna[r] = 0
                else:
                    dna[r] += 1
            else:
                if dna[r] == 0:
                    dna[r] = 0xFF
                else:
                    dna[r] -= 1
        return str(dna)


    def GetAvgAge(self):
        ageSum = 0
        for i in self.population:
            ageSum += i.age
        return float(ageSum) / len(self.population)

    def GetAvgFitness(self):
        fitnessSum = 0.0
        for i in self.population:
            fitnessSum += self.fitnessFunction(i.entity)
        return float(fitnessSum) / len(self.population)

    def __str__(self):
        return "curr population: %2d | fittest: %3.2e | avg age: %4.2f | avg fitness: %3.2e" % (self.populationSize, self.fitnessFunction(self.population[0].entity), self.GetAvgAge(), self.GetAvgFitness())


def Fitness(nn):
    return nn.GetError()

def Training(nn, trainingSet, learningRate):
    nn.Train(100, trainingSet, learningRate)

trainingSet = NN.PrepareTrainingSet(3, [ NN.TrainingSet(operation="xor", input=(0.0, 0.0), output=(0.0,)),
                NN.TrainingSet(operation="xor", input=(0.0, 1.0), output=(1.0,)),
                NN.TrainingSet(operation="xor", input=(1.0, 0.0), output=(1.0,)),
                NN.TrainingSet(operation="xor", input=(1.0, 1.0), output=(0.0,))])

g = Genetic(lambda encoding: NN.NeuralNet(4, 3, encoding),
            lambda nn: Fitness(nn),
            lambda nn: Training(nn, trainingSet, 1.0),
            20,
            0.1,
            0.1)

for i in range(10):
    g.NextGeneration()
    print g
print g.GetFittest().GetResults(trainingSet)
