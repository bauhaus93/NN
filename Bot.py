import random

from math import sin, cos, pi, degrees, radians

import NN

class Bot:

    def __init__(self, nn = None, layers = 0, units = 0, color = (0xFF, 0xFF, 0xFF), size = 3):
        if nn is None:
            self.nn = NN.NeuralNet(layers, units)
        else:
            self.nn = nn

        self.color = color
        self.size = size

        self.rotation = 0.0
        self.x = 0.0
        self.y = 0.0
        self.viewRadius = 4 * self.size
        self.speed = 1 + random.random()
        self.turningSpeed = 2 * pi / 40.0

    def SetPos(self, (x, y)):
        self.x = x
        self.y = y

    def SetRotation(self, angle):
        self.rotation = angle

    def RandomizeRotation(self):
        self.rotation = 2 * pi * random.random()

    def RandomizeColor(self):
        self.color = (random.randint(0, 0xFF), random.randint(0, 0xFF), random.randint(0, 0xFF))

    def RandomizePosition(self, rect):
        self.x = random.randint(rect[0], rect[2])
        self.y = random.randint(rect[1], rect[3])

    def Rotate(self, rad):
        self.rotation += rad
        if self.rotation > 2 * pi:
            self.rotation -= 2 * pi
        elif self.rotation < 0:
            self.rotation += 2 * pi

    def GetPos(self):
        return (int(self.x), int(self.y))

    def GetRotation(self):
        return self.rotation

    def GetColor(self):
        return self.color

    def GetSize(self):
        return self.size

    def GetViewRadius(self):
        return self.viewRadius

    def GetActions(self):
        return self.nn.GetOutput()

    def InBoundaries(self, rect):
        return all((self.x >= rect[0], self.y >= rect[1], self.x < rect[2], self.y < rect[3]))

    def Move(self, units):
        relX = units * cos(self.rotation)
        relY = units * sin(self.rotation)
        self.x += relX
        self.y += relY

    def Process(self, environment):
        actions = self.nn.FeedForward(environment)

        if actions[0] > 0.75 and actions[0] > actions[1]:
            self.Rotate(self.turningSpeed)
        elif actions[1] > 0.75 and actions[1] > actions[0]:
            self.Rotate(-self.turningSpeed)

        self.Move(self.speed)

        return actions

    def GiveFeedback(self, feedback):
        self.nn.Backpropagate(feedback, 1.0)
