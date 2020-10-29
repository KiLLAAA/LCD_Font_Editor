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
class FontWidget(wx.Panel):
    ################
    # INIT PANEL
    def __init__(self, mainwindow, parent, bytewidth, mode=0):
        # Initial values
        self.modes = [{"id" : 0, "zoom" : 2, "name" :"Dotted pixels", "method" : 0}, {"id" : 1, "zoom" : 2, "name" :"Full pixels", "method" : 1}, {"id" : 2, "zoom" : 1, "name" :"Micro", "method" : 0}] # method > 0 pixel / 1 rect
        self.selectedMode = mode
        self.fieldSize = 256 # initial, gets set after input got parsed, max selected index = fieldSize -1
        self.glyphsHorizontal = 16 # initial, gets set after input got parsed
        self.glyphsVertical = 16 # initial, gets set after input got parsed
        self.pixel_diameter = self.modes[self.selectedMode]["zoom"] # how large is a pixel aka zoom
        self.font_bytewidth = bytewidth # bytes per glyph
        self.data = [0] * (self.fieldSize * self.font_bytewidth) # initial placeholder data, gets loaded after input got parsed
        self.highlightedCell = (0, 0)
        self.selectedCell = (0, 0)
        # Panel size
        self.width = bytewidth * self.glyphsHorizontal * self.pixel_diameter
        self.height = 8 * self.glyphsVertical * self.pixel_diameter
        # Init panel
        wx.Panel.__init__(self, parent, size=(self.width, self.height))
        self.parent = parent
        self.mainwindow = mainwindow
        self.debug = self.mainwindow.debugInfo # debug info goes to main
        # colours
        self.SetBackgroundColour("#000000")
        self.colourActiveNormal = "#FFFFFF" # DEFAULT
        self.colourActiveSelected = "#FF0000" # DEFAULT
        self.colourActiveHighlight = "#00FF00" # DEFAULT
        # Bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_MOTION, self.onMouseMove)

    ################
    # SET INTERNALS
    def setByteWidth(self, bytewidth):
        """Set font width"""
        self.font_bytewidth = bytewidth
        # update values, resize panel and layout its sizer
        self.width = self.font_bytewidth * self.glyphsHorizontal * self.pixel_diameter
        self.height = 8 * self.glyphsVertical * self.pixel_diameter # 8 hardcoded! -> byte len = font height
        self.SetMinSize(wx.Size(self.width, self.height))
        self.GetParent().Layout()
        self.GetParent().GetParent().Layout()

    def setFieldSize(self, size):
        """Set field size"""
        if size < 1:
            self.debug("Font widget", "> setFieldSize", size)
            size = 1 # prevent 0
        self.fieldSize = size
        glyphsVertical = size / 16
        if size < 16 :
            glyphsHorizontal = size
        elif size >= 16:
            glyphsHorizontal = 16
        if size % glyphsHorizontal > 0 : glyphsVertical = glyphsVertical + 1

        if glyphsHorizontal < 1 : glyphsHorizontal = 1
        if glyphsVertical < 1 : glyphsVertical = 1

        self.glyphsHorizontal, self.glyphsVertical = glyphsHorizontal, glyphsVertical
        self.debug("FontWidget", "> new size", size, "> set to", self.glyphsHorizontal, "x", self.glyphsVertical)
        # Calculate size, resize panel and layout its sizer
        self.width = self.font_bytewidth * self.glyphsHorizontal * self.pixel_diameter
        self.height = 8 * self.glyphsVertical * self.pixel_diameter # 8 hardcoded! -> byte len = font height
        self.SetMinSize(wx.Size(self.width, self.height))
        self.GetParent().Layout()
        self.GetParent().GetParent().Layout()

    def setActiveColours(self, normal, selected, highlight):
        """Set colours of active pixels"""
        self.colourActiveNormal = normal
        self.colourActiveSelected = selected
        self.colourActiveHighlight = highlight

    ################
    # SET AND GET INDEX
    def setSelectedIndex(self, index):
        """Set selected glyph index"""
        self.selectedCell = self.indexToCell(index)
        #self.debug("FontWidget", "> setSelectedIndex > selectedCell", self.selectedCell)

    def getSelectedIndex(self):
        """Returns int selected glyph index"""
        index = self.cellToIndex(self.selectedCell)
        #self.debug("FontWidget", "> getSelectedIndex > selected cell", self.selectedCell, "> cell to index", index)
        return index

    ################
    # SET AND GET MODES
    def getModesAvailable(self):
        """Returns list of dicts containing display modes"""
        return self.modes

    def setMode(self, mode):
        """Set display mode"""
        self.selectedMode = mode
        # Panel size
        self.pixel_diameter = self.modes[self.selectedMode]["zoom"]
        # Calculate size, resize panel and layout its sizer
        self.width = self.font_bytewidth * self.glyphsHorizontal * self.pixel_diameter
        self.height = 8 * self.glyphsVertical * self.pixel_diameter # 8 hardcoded! -> byte len = font height
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
        self.debug("FontWidget", "Event", "Paint")
        dc = wx.PaintDC(self)
        dc.SetAxisOrientation(True, False)

        for gy in range(0, self.glyphsVertical):
          for gx in range(0, self.glyphsHorizontal):
            pixelColour = self.colourActiveNormal # DEFAULT "#FFFFFF"
            backColour = "#000000"

            if (gx, gy) == self.highlightedCell:
                pixelColour = self.colourActiveHighlight # DEFAULT "#00FF00"
                backColour = "#666666" # bylo 333

            if (gx, gy) == self.selectedCell:
                pixelColour = self.colourActiveSelected # DEFAULT "#FF0000"
                backColour = "#333333"

            #if self.cellToIndex((gx, gy)) > (self.fieldSize - 1):

            for xx in range(0, self.font_bytewidth):
              indexx = ((gy * (self.font_bytewidth * self.glyphsHorizontal))+ (self.font_bytewidth * gx)) +xx
              if indexx < len(self.data):
                  data = self.data[((gy * (self.font_bytewidth * self.glyphsHorizontal))+ (self.font_bytewidth * gx)) +xx] # may not get out of range
              else:
                  data = 0
                  # mark where is no data > when are one or more items on next line, like 17 glyphs, 16 on line1 , 1 on line2 + 15 empty grey marked
                  pixelColour = "#4f5049"
                  backColour = "#4f5049"
              #self.debug("index", indexx, "data", data)
              if isinstance(data, str):
                data = int(data, 16) # int conversion done here, init can be done with list of ints, new data can be given as list of hex strings
              #self.debug("data type>>>>>>>>>>>", str(type(data)))
              for yy in range(0, 8):
                currentColour = backColour
                if (data & (1<<(yy))) :
                    currentColour = pixelColour
                    # drawing only active pixels was not much faster on Atom - left for future tests
                    #dc.SetPen(wx.Pen(currentColour)) # single pixel colour
                    #dc.SetBrush(wx.Brush(currentColour)) #
                    #dc.DrawRectangle((gx*self.font_bytewidth * self.pixel_diameter)+(xx * self.pixel_diameter), (gy*8 * self.pixel_diameter)+(yy * self.pixel_diameter), self.pixel_diameter, self.pixel_diameter)
                    #dc.DrawPoint((gx*self.font_bytewidth * self.pixel_diameter)+(xx * self.pixel_diameter), (gy*8 * self.pixel_diameter)+(yy * self.pixel_diameter))
                dc.SetPen(wx.Pen(currentColour))
                dc.SetBrush(wx.Brush(currentColour))
                if self.modes[self.selectedMode]["method"] == 0: dc.DrawPoint((gx*self.font_bytewidth * self.pixel_diameter)+(xx * self.pixel_diameter), (gy*8 * self.pixel_diameter)+(yy * self.pixel_diameter))
                elif self.modes[self.selectedMode]["method"] == 1: dc.DrawRectangle((gx*self.font_bytewidth * self.pixel_diameter)+(xx * self.pixel_diameter), (gy*8 * self.pixel_diameter)+(yy * self.pixel_diameter), self.pixel_diameter, self.pixel_diameter)
                
                
    ################
    # MOUSE EVENTS
    def onMouseEnter(self, event):
        """Event mouse entered widget"""
        self._mouseIn = True
        self.debug("FontWidget", "Event", "MouseEnter")

    def onMouseLeave(self, event):
        """Event mouse left widget"""
        self._mouseIn = False
        self.highlightedCell = None
        self.debug("FontWidget", "Event", "MouseLeave")

    def onMouseMove(self, event):
        """Event mouse move"""
        pt = event.GetPosition()
        xx, yy = pt
        if (xx < 0) or (yy < 0): return # event sometimes gives values outside the draw area causing weird bugs
        if xx > (self.width-1): return # event sometimes gives values outside the draw area causing weird bugs # -1 stands for last pix
        if yy > (self.height-1): return # event sometimes gives values outside the draw area causing weird bugs # -1 stands for last pix

        previousHighlighted = self.highlightedCell
        #self.highlightedCell = self.screenPositionToCell(pt)
        highlighted = self.screenPositionToIndex(pt)
        if highlighted >= (self.fieldSize - 1):
            self.debug("FontWidget", "Warning", "Event", "MouseMove", "highlighted index larger than fieldSize!", "highlighted", highlighted, "self.fieldSize", self.fieldSize)
            highlighted = (self.fieldSize - 1)
            #highlighted = None # looks bad
        #old
        #self.selectedCell = self.screenPositionToCell(pt)
        #new
        self.highlightedCell = self.indexToCell(highlighted)
        self.debug("FontWidget", "Event", "MouseMove", "hover over pixel", pt, "> highlighted index", highlighted, "> cell", self.highlightedCell)

        if self.highlightedCell != previousHighlighted:
            self.debug("FontWidget", "Event", "MouseMove", "previousHighlighted", previousHighlighted, "current highlightedCell", self.highlightedCell, "> refresh")
            self.Refresh()


    def onMouseDown(self, event):
        """Event left mouse down"""
        self.mouseDown = True
        self.debug("FontWidget", "Event", "MouseDown")

    def onMouseUp(self, event):
        """Event left mouse up"""
        # Return if no data to display
        if self.data: pass
        else: return

        self.mouseDown = False

        pt = event.GetPosition()  # position tuple

        selected = self.screenPositionToIndex(pt)
        if selected >= (self.fieldSize - 1):
            self.debug("FontWidget", "Event", "MouseUp", "Warning", "selected index larger than fieldSize!", "selected", selected, "self.fieldSize", self.fieldSize)
            selected = (self.fieldSize - 1)

        # old
        #self.selectedCell = self.screenPositionToCell(pt)
        # new
        self.debug("FontWidget", "Event", "MouseUp > pixel",pt, "> index", selected, "> cell", self.indexToCell(selected))
        self.debug("FontWidget", "info:", "Selected glyph index >", selected)
        self.selectedCell = self.indexToCell(selected)
        self.Refresh()

    ################
    # HELPERS
    def screenPositionToCell(self, pt):
        """Returns tuple"""
        xx, yy = pt
        cell_x = xx/(self.font_bytewidth * self.pixel_diameter)
        cell_y = yy/(8 * self.pixel_diameter) # 88888888888888 HaRDCODED
        return(cell_x, cell_y)

    def screenPositionToIndex(self, pt):
        """Returns int"""
        xx, yy = pt
        cell_x = xx / (self.font_bytewidth * self.pixel_diameter)
        cell_y = yy / (8 * self.pixel_diameter) # 88888888888888 HaRDCODED
        index = (cell_y * self.glyphsHorizontal) + cell_x
        #self.debug("FontWidget", "hover over index", index)
        return index

    def cellToIndex(self, cell):
        """Returns int"""
        if cell == None: return None # for hover!
        cell_x, cell_y = cell
        index = (cell_y * self.glyphsHorizontal) + cell_x
        #self.debug("FontWidget", "cellToIndex cell", cell , "index", index)
        return index

    def indexToCell(self, index):
        """Returns tuple"""
        #if index == None: return None
        cell_y = index / self.glyphsHorizontal
        cell_x = index % self.glyphsHorizontal
        #self.debug("FontWidget", "indexToCell", cell_x, cell_y)
        return(cell_x, cell_y)
################################################################
