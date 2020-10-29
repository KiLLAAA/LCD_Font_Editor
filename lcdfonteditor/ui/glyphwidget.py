#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2020, Lukas Vyhnalek aka KiLLA
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

################
# IMPORTS
import wx

################################################################
class GlyphWidget(wx.Panel):
    ################
    # INIT PANEL
    def __init__(self, mainwindow, parent, bytewidth, mode=0):
        # Initial values
        self.modes = [{"id" : 0, "zoom" : 16, "name" : "Big pixels & grid", "method" : 0}, {"id" : 1, "zoom" : 16, "name" : "Big pixels & no grid", "method" : 1}, {"id" : 2, "zoom" : 8, "name" : "Mid pixels & grid", "method" : 0}, {"id" : 3, "zoom" : 8, "name" : "Mid pixels & no grid", "method" : 1}, {"id" : 4, "zoom" : 4, "name" : "Small pixels & no grid", "method" : 1}]
        self.selectedMode = mode # mode selected by init
        self.data = [65, 33, 17, 9, 7] # initial placeholder data, gets loaded after input got parsed
        self.font_bytewidth = bytewidth  # bytes per glyph
        self.pixel_diameter = self.modes[self.selectedMode]["zoom"] # how large is a pixel aka zoom
        self.highlightedPixel = None
        # Panel size
        self.width = self.font_bytewidth * self.pixel_diameter
        self.height = 8 * self.pixel_diameter # 8 hardcoded! -> byte len = font height
        parent.GetParent().GetParent().debugInfo("GlyphWidget", "> initial size", self.width, self.height)
        # Init panel
        wx.Panel.__init__(self, parent, size=(self.width, self.height))
        self.parent = parent
        self.mainwindow = mainwindow
        self.debug = self.mainwindow.debugInfo # debug info goes to main
        # colours
        self.SetBackgroundColour("#4f5049") # hardcoded colour to match underlying panel
        # Bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self._onMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._onMouseLeave)
        self.Bind(wx.EVT_ENTER_WINDOW, self._onMouseEnter)
        self.Bind(wx.EVT_MOTION, self.onMouseMove)

    ################
    # SET AND GET
    def setByteWidth(self, bytewidth):
        """Set glyph width"""
        self.font_bytewidth = bytewidth
        self.width = self.font_bytewidth * self.pixel_diameter
        self.height = 8 * self.pixel_diameter # 8 hardcoded! -> byte len = font height
        self.SetMinSize(wx.Size(self.width, self.height))
        self.debug("GlyphWidget", "> SetMinSize", self.width, self.height)
        self.GetParent().Layout()

    def getModesAvailable(self):
        """Returns list of dicts containing display modes"""
        return self.modes

    def setMode(self, mode):
        """Set display mode"""
        self.selectedMode = mode
        # Panel size
        self.pixel_diameter = self.modes[self.selectedMode]["zoom"]
        # Calculate size, resize panel and layout its sizer
        self.width = self.font_bytewidth * self.pixel_diameter
        self.height = 8 * self.pixel_diameter # 8 hardcoded! -> byte len = font height
        self.SetMinSize(wx.Size(self.width, self.height))
        self.GetParent().Layout()
        self.GetParent().GetParent().Layout()
        self.Refresh()
        
    def getMode(self):
        """Returns int selcted mode"""
        return self.selectedMode
        
    ################
    # PAINT EVENT
    def OnPaint(self, event):
        """Event paint"""
        # return if no data to display
        if self.data: pass
        else: return
        self.debug("GlyphWidget", "Event", "Paint", self.data)
        dc = wx.PaintDC(self)
        dc.SetAxisOrientation(True, False)

        # for xx in range(0, self.font_bytewidth): fails when not enough data
        for xx in range(0, len(self.data)):
            data = self.data[xx] #

            if isinstance(data, str):
                data = int(data, 16) # int conversion done here to support bytearray input which gets sliced to str above
            #self.debug("data type>>>>>>>>>>>", str(type(data)))
            for yy in range(0, 8): # 8 hardcoded!
                backColour = "#000000"
                foreColour = "#FFFFFF"
                if (xx, yy) == self.highlightedPixel:
                    backColour = "#333333"
                    foreColour = "#999999"
                currentColour = backColour
                if (data & (1<<(yy))) : currentColour = foreColour # if bit is set - colour current pixel
                if self.modes[self.selectedMode]["method"] == 0: dc.SetPen(wx.Pen("#333333")) # set colour of grid between pixels
                elif self.modes[self.selectedMode]["method"] == 1: dc.SetPen(wx.TRANSPARENT_PEN) # No grid
                dc.SetBrush(wx.Brush(currentColour)) # set colour to fill rect
                dc.DrawRectangle(xx * self.pixel_diameter, yy * self.pixel_diameter, self.pixel_diameter, self.pixel_diameter)

    ################
    # USER EVENTS
    def _onMouseEnter(self, event):
        """Event mouse entered widget"""
        self.mouseIn = True
        self.debug("GlyphWidget", "Event", "MouseEnter")

    def _onMouseLeave(self, event):
        """Event mouse left widget"""
        self.mouseIn = False
        self.debug("GlyphWidget", "Event", "MouseLeave")
        self.highlightedPixel = None
        self.Refresh()

    def onMouseMove(self, event):
        """Event mouse move"""
        pt = event.GetPosition()
        xx, yy = pt
        if (xx < 0) or (yy < 0): return # event sometimes gives negative values whose cause another weird bugs
        if xx > (self.width-1): return # event sometimes gives values outside draw area, maybe border? --1 stands for last pix or another check with == would be required
        if yy > (self.height-1): return # event sometimes gives values outside draw area, maybe border?

        pixel_x = xx/self.pixel_diameter
        pixel_y = (yy/self.pixel_diameter)
        previousHighlighted = self.highlightedPixel
        self.highlightedPixel = (pixel_x, pixel_y)
        self.debug("GlyphWidget", "Event", "MouseMove > pixel", xx, yy, "> cell", self.highlightedPixel)
        if self.highlightedPixel != previousHighlighted:
            self.Refresh()

    def _onMouseDown(self, event):
        """Event left mouse down"""
        self.mouseDown = True

    def onMouseUp(self, event):
        """Event left mouse up"""
        # return if no data to display
        if self.data: pass
        else: return

        self.mouseDown = False
        pt = event.GetPosition()  # position tuple
        #self.last_LeftUp = pt
        xx, yy = pt

        if (xx < 0) or (yy < 0): return # event sometimes gives negative values whose cause another weird bugs
        if xx > (self.width-1): return # event sometimes gives values outside draw area, maybe border? --1 stands for last pix or another check with == would be required
        if yy > (self.height-1): return # event sometimes gives values outside draw area, maybe border?

        pixel_x = xx/self.pixel_diameter # cell x
        pixel_y = (yy/self.pixel_diameter) # cell y

        self.debug("GlyphWidget", "Event", "MouseUp > pixel",pt, "> cell", pixel_x, pixel_y)
        
        self.data[pixel_x] = (self.data[pixel_x] ^ (1<<pixel_y)) # NEW DATA!

        # print the data
        printable = ""
        printable += ( ', '.join("0x%02X" % (x) for x in self.data) )
        self.debug("GlyphWidget", "info:", "new data:", self.data, ">", printable)

        self.Refresh()

        #event.Skip()
################################################################
