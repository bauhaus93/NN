#!/usr/bin/python2
import pygame

import NN

def DrawNN(nn, screen, w, h):
    r = 10
    padding = 20
    dim = nn.GetDimensions()
    offX = (w - padding) / dim[0]
    offY = (h - padding) / dim[1]

    posX = padding + r
    posY = padding + r
    for layer in range(dim[0]):
        for node in range(dim[1]):

            if layer + 1 < dim[0]:
                for destNode in range(dim[1]):
                    weight = nn.GetConnection(layer, node, destNode)
                    if weight > 0:
                        color = (0, 0xFF, 0)
                    else:
                        color = (0xFF, 0, 0)
                    pygame.draw.line(screen, color, (posX, posY), (posX + offX, padding + r + offY * destNode))

            pygame.draw.circle(screen, (0xFF, 0xFF, 0xFF), (posX, posY), r)

            bias = round(nn.GetBias(layer, node), 2)
            if bias > 0:
                color = (0, 0xFF, 0)
            else:
                color = (0xFF, 0, 0)

            text = font.render(str(bias), False, color)
            screen.blit(text, (posX+r, posY-2*r))
            posY += offY
        posY = padding + r
        posX += offX


def GetError(font, errors, w, h):


    maxError = max(errors)

    surf = pygame.Surface((w, h))
    pygame.draw.rect(surf, (0xFF, 0xFF, 0xFF), (1, 1, w-1, h-1), 1)
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
    text = font.render(errStr, False, (0xFF, 0xFF, 0xFF))
    surf.blit(text, (5, 5))
    return surf

def DrawResults(screen, font, runs, results, x, y):
    h = font.size("ABC")[1]
    text = font.render("Cycles: %d" % runs, False, (0xFF, 0xFF, 0xFF), (0, 0, 0))
    screen.blit(text, (x, y))
    y +=h
    for result in results:
        text = font.render(result, False, (0xFF, 0xFF, 0xFF), (0, 0, 0))
        screen.blit(text, (x, y))
        y += h


pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(pygame.font.match_font("verdana"), 14)
done = False
screenW = pygame.display.Info().current_w
screenH = pygame.display.Info().current_h

nn = NN.NeuralNet(4, 2)

trainingSet = []
trainingSet.append(NN.TrainingSet(operation="xor", input=(0.0, 0.0), output=(0.0,)))
trainingSet.append(NN.TrainingSet(operation="xor", input=(0.0, 1.0), output=(1.0,)))
trainingSet.append(NN.TrainingSet(operation="xor", input=(1.0, 0.0), output=(1.0,)))
trainingSet.append(NN.TrainingSet(operation="xor", input=(1.0, 1.0), output=(0.0,)))

errors = []
runs = 0
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    nn.Train(trainingSet, 200, 1.0, lambda r: r * 1.0, 500)
    runs += 100
    errors.append(nn.GetError())
    if len(errors) > 2:
        errSurf = GetError(font, errors, 400, 400)
        screen.blit(errSurf, (0, 0))
        errors = errors[-100:]

    DrawResults(screen, font, runs, nn.GetResults(trainingSet), 420, 10)

    pygame.display.flip()
