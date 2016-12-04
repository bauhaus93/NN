#!/usr/bin/python2
import wx

import NN

class Panel(wx.Panel):

    def __init__(self, parent):
        super(Panel, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        if not hasattr(self, "nn"):
            return

        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        w, h = self.GetClientSize()
        r = 10
        padding = 20
        dim = self.nn.GetDimensions()
        offX = (w - padding) / dim[0]
        offY = (h - padding) / dim[1]

        posX = padding + r
        posY = padding + r
        for layer in range(dim[0]):
            for node in range(dim[1]):

                if layer + 1 < dim[0]:
                    for destNode in range(dim[1]):
                        weight = self.nn.GetConnection(layer, node, destNode)
                        if weight > 0:
                            dc.SetPen(wx.Pen((0, 0xFF, 0)))
                        else:
                            dc.SetPen(wx.Pen((0xFF, 0, 0)))
                        dc.DrawLine(posX, posY, posX + offX, padding + r + offY * destNode)

                dc.SetPen(wx.Pen((0xFF, 0xFF, 0xFF)))
                dc.DrawCircle(posX, posY, r)

                bias = round(self.nn.GetBias(layer, node), 2)
                if bias >= 0:
                    dc.SetTextForeground((0, 0xFF, 0))
                else:
                    dc.SetTextForeground((0xFF, 0, 0))
                dc.DrawText(str(bias), posX+r, posY-2*r)
                posY += offY
            posY = padding + r
            posX += offX

    def SetNetwork(self, nn):
        self.nn = nn


class Frame(wx.Frame):

    def __init__(self):
        super(Frame, self).__init__(None, wx.ID_ANY, "NN")
        self.SetClientSize((800, 600))
        self.Center()
        self.panel = Panel(self)
        self.nn = NN.NeuralNet(4, 4)
        self.panel.SetNetwork(self.nn)

app = wx.App(False)
frame = Frame()
frame.Show(True)

app.MainLoop()
