import random

from math import sin, cos

import NN

class Bot:

    def __init__(self, nn = None, layers = 0, units = 0, color = (0xFF, 0xFF, 0xFF), size = 3):
        if nn is None:
            self.nn = NN.NeuralNet(layers, units)
        else:
            self.nn = nn

        self.color = color
        self.size = size

        self.viewAngle = 0.0
        self.x = 0.0
        self.y = 0.0
        self.speed = 1 + random.random()
        self.turningSpeed = 0.05 + random.random() / 5


    def SetPos(self, (x, y)):
        self.x = x
        self.y = y

    def SetViewAngle(self, angle):
        self.viewAngle = angle

    def RandomizeAngle(self):
        self.viewAngle = random.randint(0, 359)

    def RandomizeColor(self):
        self.color = (random.randint(0, 0xFF), random.randint(0, 0xFF), random.randint(0, 0xFF))

    def RandomizePosition(self, rect):
        self.x = random.randint(rect[0], rect[2])
        self.y = random.randint(rect[1], rect[3])

    def Rotate(self, angle):
        self.viewAngle += angle
        if self.viewAngle > 360:
            self.viewAngle -= 360

    def GetPos(self):
        return (int(self.x), int(self.y))

    def GetViewAngle(self):
        return self.viewAngle

    def GetColor(self):
        return self.color

    def GetSize(self):
        return self.size

    def InBoundaries(self, rect):
        return all((self.x >= rect[0], self.y >= rect[1], self.x < rect[2], self.y < rect[3]))

    def Move(self, units):
        relX = units * sin(self.viewAngle)
        relY = units * cos(self.viewAngle)
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
