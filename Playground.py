#!/bin/python2.7

import pygame
import random

from math import sin, cos, sqrt

import Bot

def LineIntersectsCircle(lineStart, lineEnd, circlePos, radius):

    dX = lineStart[0] - lineEnd[0]
    dY = lineStart[1] - lineEnd[1]
    fX = circlePos[0] - lineStart[0]
    fY = circlePos[1] - lineStart[1]

    a = dX**2 + dY**2
    b = 2 * (dX * fX + dY * fY)
    c = fX**2 + fY**2 - radius**2

    discr = b**2 - 4*a*c

    if discr < 0:
        return False

    discr = sqrt(discr)

    t1 = (-b - discr) / (2*a)
    t2 = (-b + discr) / (2*a)

    if t1 >= 0 and t1 <= 1:
        return True

    if t2 >= 0 and t2 <= 1:
        return True

    return False


class Playground:

    def __init__(self, sizeX, sizeY):
        pygame.init()
        self.screen = pygame.display.set_mode((sizeX, sizeY))
        self.fontStd = pygame.font.Font(pygame.font.match_font("verdana,dejavusans"), 14)
        self.fontBig = pygame.font.Font(pygame.font.match_font("verdana,dejavusans"), 20)
        self.screenW = pygame.display.Info().current_w
        self.screenH = pygame.display.Info().current_h

        self.bots = []
        for i in range(20):
            bot = Bot.Bot(layers = 4, units = 2, size = 10)
            bot.SetPos((random.random() * self.screenW, random.random() * self.screenH))
            bot.RandomizeAngle()
            bot.RandomizeColor()
            self.bots.append(bot)

    def Loop(self):
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            self.ProcessBots()
            self.Draw()
            pygame.time.wait(5)

    def Draw(self):
        self.screen.fill((0, 0, 0))

        for bot in self.bots:
            self.DrawBot(bot)

        pygame.display.flip()

    def DrawBot(self, bot):
        pos = bot.GetPos()
        view = bot.GetViewAngle()
        size = bot.GetSize()
        pygame.draw.line(self.screen, (0xFF, 0xFF, 0xFF), pos, (pos[0] +  (size * 4) * sin(view), pos[1] + (size * 4) * cos(view)))
        pygame.draw.circle(self.screen, bot.GetColor(), pos, size)


    def GetEnvironment(self, bot):
        x, y = bot.GetPos()
        view = bot.GetViewAngle()
        size = bot.GetSize()

        targetX = x + (size * 4) * sin(view)
        targetY = y + (size * 4) * cos(view)
        if targetX < 5 or targetX > self.screenW - 5 or targetY < 5 or targetY > self.screenH - 5:
            return (1.0, 0.0)

        for b in self.bots:
            if b != bot:
                bX, bY = b.GetPos()
                s = b.GetSize()
                if LineIntersectsCircle((x, y), (targetX, targetY), (bX, bY), s):
                    return (1.0, 0.0)

        return (0.0, 0.0)

    def ProcessBots(self):
        boundaries = (0, 0, self.screenW, self.screenH)
        for bot in self.bots:
            environment = self.GetEnvironment(bot)
            bot.Process(environment)

            if environment[0] == 1.0:
                feedback = (1.0, 0.0)
            else:
                feedback = (0.0, 0.0)
            bot.GiveFeedback(feedback)

            if not bot.InBoundaries(boundaries):
                bot.RandomizePosition((0, 0, self.screenW, self.screenH))
                bot.RandomizeAngle()


p = Playground(800, 600)
p.Loop()
