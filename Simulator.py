#!/bin/python2.7

import pygame

import NN
import Trainer

class Simulator:

    def __init__(self, sizeX, sizeY):
        pygame.init()
        self.screen = pygame.display.set_mode((sizeX, sizeY))
        self.fontStd = pygame.font.Font(pygame.font.match_font("verdana,dejavusans"), 14)
        self.fontBig = pygame.font.Font(pygame.font.match_font("verdana,dejavusans"), 20)
        self.screenW = pygame.display.Info().current_w
        self.screenH = pygame.display.Info().current_h

    def SetNetwork(self, nn, trainingSet):
        self.nn = nn
        self.trainer = Trainer.Trainer(nn, trainingSet, 2.0, lambda r: r * 0.95, 1000, 2, 1)

    def Loop(self):
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            self.ProcessNN()
            self.DrawInfo()

    def ProcessNN(self):
        self.trainer.Work(100)

    def DrawInfo(self):
        summarySurf = self.GetSummarySurface(self.screenW, 150)
        nnSurf = self.GetNNSurface(600, 600)
        errSurf = self.GetErrorSurface(400, 600)

        self.screen.blit(summarySurf, (0, 0))
        self.screen.blit(nnSurf, (0, 150))
        self.screen.blit(errSurf, (600, 150))
        pygame.display.flip()

    def GetNNSurface(self, w, h, radius=10, padding=20):
        surf = pygame.Surface((w, h))

        pygame.draw.rect(surf, (0xFF, 0xFF, 0xFF), (1, 1, w-1, h-1), 1)

        dim = self.nn.GetDimensions()
        offX = (w - padding) / dim[0]
        offY = (h - padding) / dim[1]

        posX = padding + radius
        posY = padding + radius
        for layer in range(dim[0]):
            for node in range(dim[1]):

                if layer + 1 < dim[0]:
                    for destNode in range(dim[1]):
                        weight = nn.GetConnection(layer, node, destNode)
                        if weight > 0:
                            color = (0, 0xFF, 0)
                        else:
                            color = (0xFF, 0, 0)
                        pygame.draw.line(surf, color, (posX, posY), (posX + offX, padding + radius + offY * destNode), 1)

                pygame.draw.circle(surf, (0xFF, 0xFF, 0xFF), (posX, posY), radius)

                bias = round(nn.GetBias(layer, node), 2)
                if bias > 0:
                    color = (0, 0xFF, 0)
                else:
                    color = (0xFF, 0, 0)

                text = self.fontStd.render(str(bias), False, color)
                surf.blit(text, (posX+radius, posY-2*radius))

                posY += offY

            posY = padding + radius
            posX += offX
        return surf

    def GetErrorSurface(self, w, h):
        errors = self.trainer.GetErrors()
        maxError = max(errors)

        surf = pygame.Surface((w, h))

        if len(errors) < 2:
            pygame.draw.rect(surf, (0xFF, 0xFF, 0xFF), (1, 1, w-1, h-1), 1)
            return surf
        points = []

        currX = 0
        stepX = float(w) / (len(errors))
        for e in errors:
            currY = 5 + (h - 30) * (e / maxError)
            points.append((currX, currY))
            currX += stepX

        pygame.draw.aalines(surf, (0xFF, 0xFF, 0xFF), False, points)

        if maxError < 1e-2:
            errStr = "%.3e" % maxError
        else:
            errStr = "%.3f" % maxError
        surf = pygame.transform.flip(surf, False, True)
        pygame.draw.rect(surf, (0xFF, 0xFF, 0xFF), (1, 1, w-1, h-1), 1)
        text = self.fontStd.render(errStr, False, (0xFF, 0xFF, 0xFF))
        surf.blit(text, (5, 5))
        return surf

    def GetSummarySurface(self, w, h):
        surf = pygame.Surface((w, h))
        hBig = self.fontBig.size("ABC")[1]
        hStd = self.fontStd.size("ABC")[1]

        text = self.fontBig.render(self.trainer.GetSummary(), False, (0xFF, 0xFF, 0xFF), (0, 0, 0))
        surf.blit(text, (0, 0))

        results = self.trainer.GetResults()
        posY = hBig + 5
        for result in results:
            text = self.fontStd.render(result, False, (0xFF, 0xFF, 0xFF), (0, 0, 0))
            surf.blit(text, (0, posY))
            posY += hStd + 5

        return surf


nn = NN.NeuralNet(4, 3)

trainingSet = [ NN.TrainingSet(operation="xor", input=(0.0, 0.0), output=(0.0,)),
                NN.TrainingSet(operation="xor", input=(0.0, 1.0), output=(1.0,)),
                NN.TrainingSet(operation="xor", input=(1.0, 0.0), output=(1.0,)),
                NN.TrainingSet(operation="xor", input=(1.0, 1.0), output=(0.0,))]

sim = Simulator(1024, 768)
sim.SetNetwork(nn, trainingSet)
sim.Loop()
