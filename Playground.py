#!/bin/python2.7

import pygame
import random
import time

from math import sin, cos, atan, sqrt, pi, degrees, radians

import Bot
import NN

def GetDistance(pA, pB):
    distX = pA[0] - pB[0]
    distY = pA[1] - pB[1]
    return sqrt(distX**2 + distY**2)

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

        self.ticks = 0
        self.boundaries = (0, 0, sizeX, sizeY)
        self.bots = []
        self.resets = []
        self.lastInfoUpdate = 0

        for i in range(2):
            bot = Bot.Bot(layers = 4, units = 2, size = 10)
            bot.RandomizePosition((0, 0, self.screenW, self.screenH))
            bot.RandomizeRotation()
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
            self.ticks += 1
            pygame.time.wait(5)

    def Draw(self):
        self.screen.fill((0, 0, 0))
        #pygame.draw.rect(self.screen, (0, 0, 0), (20, 20, self.screenW-40, self.screenH-40), 2)

        for bot in self.bots:
            self.DrawBot(bot)

        pygame.draw.line(self.screen, (0xFF, 0xFF, 0xFF), self.bots[0].GetPos(), self.bots[1].GetPos())
        tb1 = self.fontStd.render("bot 1", False, (0xFF, 0xFF, 0xFF), (0x2F, 0x2F, 0x2F))
        tb2 = self.fontStd.render("bot 2", False, (0xFF, 0xFF, 0xFF), (0x2F, 0x2F, 0x2F))

        self.screen.blit(tb1, self.bots[0].GetPos())
        self.screen.blit(tb2, self.bots[1].GetPos())

        currTime = time.time()
        if currTime - self.lastInfoUpdate >= 1.0 and self.ticks % 100 == 0:
            self.resets = filter(lambda t: currTime - t < 10, self.resets)

            hStd = self.fontStd.size("ABC")[1]
            h = 2 * hStd

            tt = "ticks: %d" % self.ticks
            tr = "resets/10s: %d" % len(self.resets)
            w = max(self.fontStd.size(tt)[0], self.fontStd.size(tr)[0])

            textTicks = self.fontStd.render(tt, False, (0xFF, 0xFF, 0xFF), (0x2F, 0x2F, 0x2F))
            textResets = self.fontStd.render(tr, False, (0xFF, 0xFF, 0xFF), (0x2F, 0x2F, 0x2F))

            self.infoSurf = surf = pygame.Surface((w, h))
            self.infoSurf.fill((0x2F, 0x2F, 0x2F))

            self.infoSurf.blit(textTicks, (0, 0))
            self.infoSurf.blit(textResets, (0, hStd))

            self.lastInfoUpdate = currTime
        self.screen.blit(self.infoSurf, (0, 0))
        pygame.display.flip()

    def DrawBot(self, bot):
        pos = bot.GetPos()
        rot = bot.GetRotation()
        size = bot.GetSize()
        viewRadius = bot.GetViewRadius()
        pygame.draw.line(self.screen, (0xFF, 0xFF, 0xFF), pos, (pos[0] +  viewRadius * cos(rot), pos[1] + viewRadius * sin(rot)))
        #pygame.draw.circle(self.screen, (0xFF, 0xFF, 0xFF), pos, bot.GetViewRadius(), 1)
        pygame.draw.circle(self.screen, bot.GetColor(), pos, size)


    def GetEnvironment(self, bot):
        env = self.GetWallData(bot)
        if bot == self.bots[0]:
            self.GetNearestHostile(bot)
        return env


    def GetNearestHostile(self, bot):
        botPos = bot.GetPos()
        botAngle = bot.GetRotation()

        minDist = -1

#        -x                  +x
#    -y  |---------------------
#        |   o
#        |       t
#        |
#        |
#    +y  |---------------------

        for b in self.bots:
            if b == bot:
                continue
            otherPos = b.GetPos()

            if minDist == -1:
                minDist = GetDistance(botPos, otherPos)
                distX = botPos[0] - otherPos[0]
                distY = botPos[1] - otherPos[1]

                if distX == 0:
                    if botPos[1] > otherPos[1]:
                        angle = 270.0
                    else:
                        angle = 90.0
                elif distY == 0:
                    if botPos[0] > otherPos[0]:
                        angle = 180.0
                    else:
                        angle = 0.0
                else:
                    angle = atan(distY / distX)
                print "dist: (%d/%d), angle: %.2f deg" % (distX, distY, degrees(angle))



    def GetWallData(self, bot):
        botPos = bot.GetPos()
        botAngle = bot.GetRotation()

        #left boundary
        minDist = GetDistance(botPos, (self.boundaries[0], botPos[1]))
        angle = pi - botAngle

        #top boundary
        dist = GetDistance(botPos, (botPos[0], self.boundaries[1]))
        if dist < minDist:
            minDist = dist
            angle = 3 * pi / 2 - botAngle

        #right boundary
        dist = GetDistance(botPos, (self.boundaries[2], botPos[1]))
        if dist < minDist:
            minDist = dist
            angle = 0 - botAngle

        #bottom boundary
        dist = GetDistance(botPos, (botPos[0], self.boundaries[3]))
        if dist < minDist:
            minDist = dist
            angle = pi / 2 - botAngle


        if minDist < bot.GetViewRadius():
            if abs(angle) < pi / 2:
                return (minDist, angle)
            if 2 * pi - abs(angle) < pi / 2:
                return (minDist, 2 * pi - abs(angle))

        return (0.0, 0.0)


    def CreateFeedback(self, bot, environment):
        actions = bot.GetActions()

        if environment[0] == 0.0 and environment[1] == 0.0:
            feedback = (0.0, 0.0)
        elif environment[0] > 0.0:
            if environment[1] > 0.0:
                feedback = (0.0, 1.0)
            else:
                feedback = (1.0, 0.0)
        else:
            feedback = (0.0, 0.0)

        bot.GiveFeedback(feedback)

    def ProcessBots(self):
        boundaries = (0, 0, self.screenW, self.screenH)
        for bot in self.bots:
            environment = self.GetEnvironment(bot)
            bot.Process(environment)
            self.CreateFeedback(bot, environment)

            if not bot.InBoundaries(boundaries):
                bot.RandomizePosition((0, 0, self.screenW, self.screenH))
                bot.RandomizeRotation()
                self.resets.append(time.time())


#p = Playground(800, 600)
#p.Loop()

def Test(botPos, otherPos):

    distX = botPos[0] - otherPos[0]
    distY = botPos[1] - otherPos[1]

    if distX == 0.0:
        if botPos[1] > otherPos[1]:
            angle = 3 * pi / 2
        else:
            angle = pi / 2
    elif distY == 0.0:
        if botPos[0] > otherPos[0]:
            angle = pi
        else:
            angle = 0.0
    else:
        angle = atan(distY / distX)
    print "dist: (%d/%d), angle: %.2f deg" % (distX, distY, degrees(angle))

a = (5.0, 5.0)
b = (4.0, 3.0)
for x in range(0, 10):
    for y in range(0, 10):
        print a, "->", (x, y)
        Test(a, (x, y))
