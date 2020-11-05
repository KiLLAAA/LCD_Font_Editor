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
import os
import sys

import wx

import dataprocessing.core

from glyphwidget import GlyphWidget
from fontwidget import FontWidget
from ui_options import OptionsFrame

################
# DEBUG
DEBUG = False # True / False
showInspectionWindow = False # True / False
if DEBUG and showInspectionWindow: import wx.lib.inspection # import widgets inspection tool

################################################################
######################### MAIN WINDOW ##########################
class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.platform = wx.Platform
        self.InitUI()

    ################################
    # INIT UI
    def InitUI(self):
        ################
        # BASIC SETUP
        self.debugInfo("================================================================") # print wx version to stdout
        self.debugInfo("python version ",sys.version)
        self.debugInfo("wx version ", wx.version())
        self.debugInfo("================================================================")

        if self.platform == "__WXMSW__": self.locale = wx.Locale(wx.LANGUAGE_ENGLISH) # /wx.LANGUAGE_DEFAULT/ -> Windows hack!
        self.basePath = self.getBasePath()
        self.clipboard = None

        ################
        # DATA PROCESSING
        DEFAULT_BYTEWIDTH = 5 # DEFAULT CONSTANT VALUE > for fonts 5 bytes/pixels wide

        self.processing = dataprocessing.core.DataProcessing(self, DEFAULT_BYTEWIDTH) # pass self - main window

        ################
        # WINDOW with OPTIONS & SETTINGS
        self.optionsWindow = None

        ################
        # LAYOUT PANELS
        self.mainPanel = wx.Panel(self)
        
        self.leftPanel = wx.Panel(self.mainPanel)
        self.leftPanel.SetBackgroundColour('#4f5049')

        self.buttonPanel = wx.Panel(self.leftPanel)
        self.buttonPanel.SetBackgroundColour('#cccccc')

        ################
        # GLYPH WIDGET
        self.screenWidth, self.screenHeight = wx.GetDisplaySize() # Get screen size and select smaller modes for netbooks
        self.debugInfo("Screen size:", self.screenWidth, "x", self.screenHeight)
        if self.screenHeight < 768:
            glyphWidgetMode = 2
            fonthPanelMode = 2
        else:
            glyphWidgetMode = 0
            fonthPanelMode = 0

        self.glyphWidget = GlyphWidget(self, self.leftPanel, DEFAULT_BYTEWIDTH, glyphWidgetMode)
        self.glyphWidget.Bind(wx.EVT_LEFT_UP, self.onGlyphWidgetMouseUp)
        self.glyphWidget.Bind(wx.EVT_LEFT_DOWN, self.onGlyphWidgetMouseDown)
        self.glyphWidget.Bind(wx.EVT_MOTION, self.onGlyphWidgetMouseMove)

        ################
        # FONT WIDGET
        ColourActiveSelected = "#cc0000" #OPTIONAL "#cc0033" "#a800a8" #FF0033
        ColourActiveHighlighted = "#00cc00" # OPTIONAL "#00cc99" "#00A8A8" #00FFCC
        self.fontWidget = FontWidget(self, self.leftPanel, DEFAULT_BYTEWIDTH, fonthPanelMode)
        #self.fontWidget.setActiveColours("#FFFFFF", ColourActiveSelected, ColourActiveHighlighted)
        self.fontWidget.Bind(wx.EVT_LEFT_UP, self.onFontWidgetMouseUp)
        self.fontWidget.Bind(wx.EVT_MOTION, self.onFontWidgetMouseMove)
        self.fontWidget.Bind(wx.EVT_LEAVE_WINDOW, self.onFontWidgetMouseLeave)

        ################
        # BUTTON PANEL SIZER
        self.buttonsGridSizer = wx.GridBagSizer(1, 1)

        ################
        # MOVE BUTTONS
        self.bmpArrowUp = wx.Bitmap(os.path.join(self.basePath, "icons", "up-arrow.png"), wx.BITMAP_TYPE_PNG)
        self.bmpArrowLeft = wx.Bitmap(os.path.join(self.basePath, "icons", "left-arrow.png"), wx.BITMAP_TYPE_PNG)
        self.bmpArrowRight = wx.Bitmap(os.path.join(self.basePath, "icons", "right-arrow.png"), wx.BITMAP_TYPE_PNG)
        self.bmpArrowDown = wx.Bitmap(os.path.join(self.basePath, "icons", "down-arrow.png"), wx.BITMAP_TYPE_PNG)

        self.moveUpButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.bmpArrowUp, size=wx.DefaultSize)
        self.moveUpButton.identifier = "moveup"
        self.moveUpButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.moveUpButton.SetToolTip(wx.ToolTip("Move up"))
        self.buttonsGridSizer.Add(self.moveUpButton, pos = (0, 1), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4) # ↑

        self.moveDownButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.bmpArrowDown, size=wx.DefaultSize)
        self.moveDownButton.identifier = "movedown"
        self.moveDownButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.moveDownButton.SetToolTip(wx.ToolTip("Move down"))
        self.buttonsGridSizer.Add(self.moveDownButton, pos = (2, 1), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4) # ↓

        self.moveLeftButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.bmpArrowLeft, size=wx.DefaultSize)
        self.moveLeftButton.identifier = "moveleft"
        self.moveLeftButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.moveLeftButton.SetToolTip(wx.ToolTip("Move left"))
        self.buttonsGridSizer.Add(self.moveLeftButton, pos = (1, 0), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4) # ←

        self.moveRightButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.bmpArrowRight, size=wx.DefaultSize)
        self.moveRightButton.identifier = "moveright"
        self.moveRightButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.moveRightButton.SetToolTip(wx.ToolTip("Move right"))
        self.buttonsGridSizer.Add(self.moveRightButton, pos = (1, 2), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4) # →

        ################
        # ACTION BUTTONS
        self.copyButtonBmp = wx.Bitmap(os.path.join(self.basePath, "icons", "copy-square.png"), wx.BITMAP_TYPE_PNG)
        self.copyButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.copyButtonBmp, size=wx.DefaultSize)
        self.copyButton.identifier = "copy"
        self.copyButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.copyButton.SetToolTip(wx.ToolTip("Copy glyph"))
        self.buttonsGridSizer.Add(self.copyButton, pos = (2, 0), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4)

        self.pasteButtonBmp = wx.Bitmap(os.path.join(self.basePath, "icons", "download-square.png"), wx.BITMAP_TYPE_PNG)
        self.pasteButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.pasteButtonBmp, size=wx.DefaultSize)
        self.pasteButton.identifier = "paste"
        self.pasteButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.pasteButton.SetToolTip(wx.ToolTip("Paste glyph"))
        self.buttonsGridSizer.Add(self.pasteButton, pos = (2, 2), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4)

        self.clearButtonBmp = wx.Bitmap(os.path.join(self.basePath, "icons", "sun-light-theme.png"), wx.BITMAP_TYPE_PNG)
        self.clearButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.clearButtonBmp, size=wx.DefaultSize)
        self.clearButton.identifier = "clear"
        self.clearButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.clearButton.SetToolTip(wx.ToolTip("Clear glyph"))
        self.buttonsGridSizer.Add(self.clearButton, pos = (1, 1), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4)

        self.moreButtonBmp = wx.Bitmap(os.path.join(self.basePath, "icons", "more.png"), wx.BITMAP_TYPE_PNG)
        self.moreButton = wx.BitmapButton(self.buttonPanel, id = wx.ID_ANY, bitmap = self.moreButtonBmp, size=wx.DefaultSize)
        self.moreButton.identifier = "more"
        self.moreButton.Bind(wx.EVT_BUTTON, self.onButtons)
        self.moreButton.SetToolTip(wx.ToolTip("Open Options & Settings window"))
        self.buttonsGridSizer.Add(self.moreButton, pos = (0, 2), span = (1, 1), flag = wx.ALL|wx.CENTER, border = 4)
        
        self.buttonPanel.SetSizer(self.buttonsGridSizer)

        ################
        # INDICATOR PANEL
        self.indicatorLabelModes = [{"id" : 0, "name" : "index", "selectedtootip" : "Selected glyph index", "hovertooltip" : "Highlighted glyph index"}, {"id" : 0, "name" : "hexindex", "selectedtootip" : "Selected glyph base 16 index", "hovertooltip" : "Highlighted glyph base 16 index"}, {"id" : 0, "name" : "character", "selectedtootip" : "Selected glyph char in ascii encoding", "hovertooltip" : "Highlighted glyph char in ascii encoding"}] # ascii hardcoded > gets changed with encoding selection
        self.indicatorSelectedLabelMode = 0 # DEFAULT
        self.indicatorPanelEncodings = [{"name":"ascii"}, {"name":"utf8"}, {"name":"iso-8859-1"}, {"name":"iso-8859-2"}, {"name":"iso-8859-3"}, {"name":"iso-8859-4"}, {"name":"iso-8859-5"}, {"name":"iso-8859-6"}, {"name":"iso-8859-7"}, {"name":"iso-8859-8"}, {"name":"iso-8859-9"}, {"name":"iso-8859-10"}, {"name":"iso-8859-13"}, {"name":"iso-8859-14"}, {"name":"iso-8859-15"}, {"name":"windows-1250"}, {"name":"windows-1251"}, {"name":"windows-1252"}, {"name":"windows-1253"}, {"name":"windows-1254"}, {"name":"windows-1255"}, {"name":"windows-1256"}, {"name":"windows-1257"}, {"name":"windows-1258"}]
        self.selectedIndicatorPanelEncoding = 0 # DEFAULT

        # colours
        self.indicatorPanelColourActiveSelected = ColourActiveSelected # OPTIONAL "#cc0033" "#a800a8"
        self.indicatorPanelColourActiveHighlighted = ColourActiveHighlighted # OPTIONAL "#00cc99" "#00A8A8"

        self.indicatorPanel = wx.Panel(self.leftPanel)
        self.indicatorPanel.Bind(wx.EVT_LEFT_UP, self.onIndicatorPanelMouseUp)
        self.indicatorPanel.SetBackgroundColour('#cccccc') # HARDCODED COLOUR
        self.indicatorPanel.SetToolTip(wx.ToolTip("Indicator, click to toggle mode"))
        self.indicatorSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.selectedLabel = wx.StaticText(self.indicatorPanel)
        self.hoverLabel = wx.StaticText(self.indicatorPanel, style=wx.ALIGN_RIGHT)

        font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD) # wx.FONTFAMILY_DEFAULT
        self.selectedLabel.SetFont(font)
        self.selectedLabel.SetForegroundColour(self.indicatorPanelColourActiveSelected) # DEFAULT "#00cc99"
        self.selectedLabel.SetLabel(self.indicatorPanelLabelFormat(self.processing.getSelectedGlyphIndex()))
        self.selectedLabel.SetToolTip(wx.ToolTip("Selected glyph index, click to toggle mode"))
        self.selectedLabel.Bind(wx.EVT_LEFT_UP, self.onIndicatorPanelMouseUp)
        self.selectedLabel.SetMinSize ((60, -1)) # set min width only to prevent too small click area

        self.hoverLabel.SetFont(font)
        self.hoverLabel.SetForegroundColour(self.indicatorPanelColourActiveHighlighted) # DEFAULT "#cc0033"
        self.hoverLabel.SetLabel(self.indicatorPanelLabelFormat(self.fontWidget.cellToIndex(self.fontWidget.highlightedCell)))
        self.hoverLabel.SetToolTip(wx.ToolTip("Highlighted glyph index, click to toggle mode"))
        self.hoverLabel.Bind(wx.EVT_LEFT_UP, self.onIndicatorPanelMouseUp)
        self.hoverLabel.SetMinSize ((60, -1)) # set min width only to prevent too small click area

        self.indicatorSizer.Add(self.selectedLabel, 0,wx.ALL|wx.ALIGN_CENTER_VERTICAL, 10) 
        self.indicatorSizer.Add(self.hoverLabel, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)

        #self.indicatorSizer.SetMinSize ((160, 32))
        # https://wxpython.org/Phoenix/docs/html/wx.Sizer.html#wx.Sizer.GetMinSize
        self.debugInfo("ui", "IndicatorPanel", "> indicator sizer > GetMinSize", self.indicatorSizer.GetMinSize())
        self.indicatorPanel.SetSizer(self.indicatorSizer) 

        ################
        # LEFT PANEL SIZER
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.glyphWidget, 0, wx.ALL|wx.CENTER, 20)
        self.mainSizer.Add(self.buttonPanel, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 20)
        self.mainSizer.Add(self.indicatorPanel, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 6)
        self.mainSizer.Add(self.fontWidget, 0,  wx.BOTTOM | wx.LEFT  |wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 20)
        self.leftPanel.SetSizer(self.mainSizer)

        ################
        # TEXT FIELD
        self.textCtrlModes = self.modes = [{"id" : 0, "name" : "Smart (fast)", "method" : 0}, {"id" : 1, "name" : "Simple (failsafe)", "method" : 1}, {"id" : 2, "name" : "Full redraw (slow)", "method" : 2}]
        self.selectedTextCtrlMode = 0 # DEFAULT mode > Smart
        self.ignoreTextEvent = False

        self.textCtrl = wx.TextCtrl(self.mainPanel, size = (320,320), style = wx.TE_MULTILINE | wx.TE_RICH) # another windows hack -> wx.TE_RICH
        textCtrlFont = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) # wx.FONTFAMILY_TELETYPE -> monospace
        self.textCtrl.SetFont(textCtrlFont)
        self.textCtrl.Bind(wx.EVT_TEXT,self.OnKeyTyped) # EVT_TEXT_ENTER, EVT_TEXT, wx.EVT_CHAR

        ################
        # MAIN SIZER
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.leftPanel, 0,  wx.LEFT | wx.TOP, 20)
        self.mainSizer.Add(self.textCtrl, 1,  wx.TOP | wx.BOTTOM | wx.LEFT | wx.EXPAND, 20)

        self.mainPanel.SetSizer(self.mainSizer)

        ################
        # WINDOW RELATED STUFF
        self.SetSize((640, 700))
        self.SetTitle("LCD Font Editor")
        self.icon = wx.IconFromBitmap(wx.Bitmap(os.path.join(self.basePath, "icons", "edit-square.png"), wx.BITMAP_TYPE_PNG))
        self.SetIcon(self.icon)
        self.Centre()
        #self.mainSizer.Fit(self) # make sizer resize parent window to best size # optional, hardcoded size looks better, on 600px screen height window size fits itself

################################################################
########################### METHODS ############################

    ################################
    # EVENTS

    ################
    # BUTTON EVENTS
    def onButtons(self, event):
        """Process events of all buttons including Options window"""
        btn = event.GetEventObject()
        self.debugInfo("ui", "Event", "Button > %s" % (event.GetEventObject().identifier))

        # recognize button and performa action
        if event.GetEventObject().identifier == "copy":
            self.debugInfo("ui", "info:", "Button", "copy data >", self.glyphWidget.data)
            self.clipboard = list(self.glyphWidget.data) # copy data

        elif event.GetEventObject().identifier == "paste":
            if self.clipboard == None: return
            #self.glyphWidget.data = list(self.clipboard) # copy data with no check - future use with SetData
            self.glyphWidget.data = list(self.clipboard) + [0] * (self.processing.getFontByteWidth() - len(list(self.clipboard))) # add missing data if font byte width changed between copy/paste
            self.debugInfo("ui", "info:", "Button", "paste data >", self.clipboard, "> new data", self.glyphWidget.data)
            self.glyphWidget.Refresh()
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

        elif event.GetEventObject().identifier == "clear":
            self.glyphWidget.data = [0] * self.processing.getFontByteWidth() # set zero
            self.glyphWidget.Refresh()
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

        elif event.GetEventObject().identifier == "more":
            if not self.optionsWindow:
                buttonsPanelPositionX, buttonsPanelPositionY = self.buttonPanel.GetScreenPosition()
                buttonsPanelSizeX, buttonsPanelSizeY = self.buttonPanel.GetSize()
                position = (buttonsPanelPositionX + buttonsPanelSizeX, buttonsPanelPositionY) # position next to buttonsPanel
                self.optionsWindow = OptionsFrame(self, position) # 
                self.optionsWindow.Show()
            else:
                self.optionsWindow.Close()

        elif event.GetEventObject().identifier == "moveup":
            self.glyphWidget.data = [ (byte>>1) for byte in self.glyphWidget.data]  # DESTRUCTIVE
            self.glyphWidget.Refresh()
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

        elif event.GetEventObject().identifier == "movedown":
            self.glyphWidget.data = [ ((byte<<1)& 0xFF) for byte in self.glyphWidget.data]  # DESTRUCTIVE
            self.glyphWidget.Refresh()
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

        elif event.GetEventObject().identifier == "moveleft":
            #self.glyphWidget.data = self.glyphWidget.data[1:] + [self.glyphWidget.data[0]] # NONDESTRUCTIVE
            self.glyphWidget.data = self.glyphWidget.data[1:] + [0] # DESTRUCTIVE
            self.glyphWidget.Refresh()
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

        elif event.GetEventObject().identifier == "moveright":
            #self.glyphWidget.data = [self.glyphWidget.data[-1]] + self.glyphWidget.data[:-1] # NONDESTRUCTIVE
            self.glyphWidget.data = [0] + self.glyphWidget.data[:-1] # DESTRUCTIVE
            self.glyphWidget.Refresh()
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

        elif event.GetEventObject().identifier == "insertright":
            self.processing.insertToRight()
            self.setWidgetsByteWidth()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()
            self.loadGlyphWidgetImageData()
            self.glyphWidget.Refresh()

            newString = self.processing.getCompleteString()
            self.textCtrl.ChangeValue(newString)

        elif event.GetEventObject().identifier == "insertleft":
            self.processing.insertToLeft()
            self.setWidgetsByteWidth()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()
            self.loadGlyphWidgetImageData()
            self.glyphWidget.Refresh()
            
            newString = self.processing.getCompleteString()
            self.textCtrl.ChangeValue(newString)

        elif event.GetEventObject().identifier == "removeright":
            self.processing.eraseFromRight()
            self.setWidgetsByteWidth()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()
            self.loadGlyphWidgetImageData()
            self.glyphWidget.Refresh()

            newString = self.processing.getCompleteString()
            self.textCtrl.ChangeValue(newString)

        elif event.GetEventObject().identifier == "removeleft":
            self.processing.eraseFromLeft()
            self.setWidgetsByteWidth()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()
            self.loadGlyphWidgetImageData()
            self.glyphWidget.Refresh()

            newString = self.processing.getCompleteString()
            self.textCtrl.ChangeValue(newString)

    ################
    # MOUSE EVENTS
    def onGlyphWidgetMouseDown(self, event):
        """onMouseDown-parent"""
        self.glyphWidget.onMouseDown(event)
        self.updateSelectedGlyph()
        self.loadFontWidgetImageData()
        self.fontWidget.Refresh()

    def onGlyphWidgetMouseUp(self, event):
        """onMouseUp-parent"""
        self.glyphWidget.onMouseUp(event)

    def onGlyphWidgetMouseMove(self, event):
        """onMouseMove-parent"""
        if self.glyphWidget.onMouseMove(event):
            self.updateSelectedGlyph()
            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

    def onFontWidgetMouseUp(self, event):
        """onFontWidgetMouseUp"""
        self.fontWidget.onMouseUp(event)
        self.processing.setSelectedGlyphIndex(self.fontWidget.getSelectedIndex()) #
        self.selectedLabel.SetLabel(self.indicatorPanelLabelFormat(self.processing.getSelectedGlyphIndex()))
        self.loadGlyphWidgetImageData() # load glyph image
        self.fontWidget.Refresh()
        self.glyphWidget.Refresh()

        self.selectedLabel.GetParent().GetContainingSizer().Layout()
        self.fontWidget.GetContainingSizer().Layout()

    def onFontWidgetMouseMove(self, event):
        """onFontWidgetMouseMove"""
        self.fontWidget.onMouseMove(event)
        # Hover label refresh
        self.hoverLabel.SetLabel(self.indicatorPanelLabelFormat(self.fontWidget.cellToIndex(self.fontWidget.highlightedCell)))
        self.hoverLabel.GetParent().GetContainingSizer().Layout()
        #self.fontWidget.Refresh() # unnecessary refresh > handled in FontWidget

    def onFontWidgetMouseLeave(self, event):
        """ """
        self.fontWidget.onMouseLeave(event)
        self.hoverLabel.SetLabel("") # Empty
        self.hoverLabel.GetParent().GetContainingSizer().Layout()
        self.fontWidget.Refresh()

    def onIndicatorPanelMouseUp(self, event):
        """Toggle mode of indicator panel"""
        if self.indicatorSelectedLabelMode == 2: self.indicatorSelectedLabelMode = 0
        else: self.indicatorSelectedLabelMode += 1
        self.selectedLabel.SetLabel(self.indicatorPanelLabelFormat(self.processing.getSelectedGlyphIndex()))
        #self.selectedLabel.Refresh()
        # Update ToolTips - those are tied to mode selected
        self.selectedLabel.SetToolTip(wx.ToolTip(self.indicatorLabelModes[self.indicatorSelectedLabelMode]["selectedtootip"]))
        self.hoverLabel.SetToolTip(wx.ToolTip(self.indicatorLabelModes[self.indicatorSelectedLabelMode]["hovertooltip"]))

    ################
    # TEXT FIELD EVENTS
    def OnKeyTyped(self, event):
        """TextCtrl changed event, parse new data"""
        #self.debugInfo("ui", "Event", "OnKeyTyped") # ultra verbose while text updates

        if not self.ignoreTextEvent:
            tempData = self.textCtrl.GetValue() # get string from TextCtrl
            self.debugInfo("New textfield input\n", tempData, "\n")

            # process import
            self.processing.importData(tempData) #  <-------------------------------------------------------- import -> parse data
            self.setWidgetsByteWidth()
            self.fontWidget.setFieldSize(self.processing.getGlyphCount()) # SET FONT WIDGET SIZE
            self.fontWidget.setSelectedIndex(self.processing.getSelectedGlyphIndex())
            
            self.loadGlyphWidgetImageData()
            self.glyphWidget.Refresh()

            self.loadFontWidgetImageData()
            self.fontWidget.Refresh()

            self.selectedLabel.SetLabel(self.indicatorPanelLabelFormat(self.processing.getSelectedGlyphIndex()))
            self.selectedLabel.GetParent().GetContainingSizer().Layout()
        else:
            pass
            #self.debugInfo("Text event skip!") # very verbose while TextCtrl updates

    ################################
    # SETTERS AND GETTERS
    def setWidgetsByteWidth(self):
        """Sets byte width to all widgets using it to match data"""
        self.glyphWidget.setByteWidth(self.processing.getFontByteWidth())
        self.fontWidget.setByteWidth(self.processing.getFontByteWidth())

    # FontWidget
    def getFontWidgetModesAvailable(self):
        """For purpose of Options window - returns list of dicts"""
        return self.fontWidget.getModesAvailable()

    def setFontWidgetMode(self, mode):
        """Set mode of font widget"""
        self.fontWidget.setMode(mode)

    def getFontWidgetMode(self):
        """Returns int mode of font widget"""
        return self.fontWidget.getMode()

    # IndicatorPanel
    def setIndicatorPanelActiveColours(self, selected, highlighted):
        """Set colours of indicator panel"""
        self.indicatorPanelColourActiveSelected = selected
        self.indicatorPanelColourActiveHighlighted = highlighted

    def getIndicatorPanelEncodingsAvailable(self):
        """For purpose of Options window - returns list of dicts"""
        return self.indicatorPanelEncodings

    def setIndicatorPanelLabelsEncoding(self, encoding):
        """Set indicator panel labels encoding"""
        self.selectedIndicatorPanelEncoding = encoding
        # Selected label refresh
        self.selectedLabel.SetLabel(self.indicatorPanelLabelFormat(self.processing.getSelectedGlyphIndex()))
        # Update ToolTips
        self.indicatorLabelModes[2]["selectedtootip"] = "Selected glyph char in %s encoding" % self.indicatorPanelEncodings[self.selectedIndicatorPanelEncoding]["name"] # updatae dict with new value
        self.indicatorLabelModes[2]["hovertooltip"] = "Highlighted glyph char in %s encoding" % self.indicatorPanelEncodings[self.selectedIndicatorPanelEncoding]["name"] # updatae dict with new value
        self.selectedLabel.SetToolTip(wx.ToolTip(self.indicatorLabelModes[self.indicatorSelectedLabelMode]["selectedtootip"]))
        self.hoverLabel.SetToolTip(wx.ToolTip(self.indicatorLabelModes[self.indicatorSelectedLabelMode]["hovertooltip"]))
        #self.selectedLabel.Refresh()
        # Hover label refresh
        self.hoverLabel.SetLabel(self.indicatorPanelLabelFormat(self.fontWidget.cellToIndex(self.fontWidget.highlightedCell)))
        self.hoverLabel.GetParent().GetContainingSizer().Layout()

    # TextCtrl
    def getTextCtrlModesAvailable(self):
        """For purpose of Options window - returns list of dicts"""
        return self.textCtrlModes

    def setTextCtrlMode(self, mode):
        """Set TextCtrl Mode"""
        self.selectedTextCtrlMode = mode

    def getTextCtrlMode(self):
        """Returns int TextCtrl Mode"""
        return self.selectedTextCtrlMode

    # GlyphWidget
    def getGlyphWidgetModesAvailable(self):
        """For purpose of Options window - returns list of dicts"""
        return self.glyphWidget.getModesAvailable()
        
    def setGlyphWidgetMode(self, mode):
        """Set mode of Font Panel"""
        self.glyphWidget.setMode(mode)
        
    def getGlyphWidgetMode(self):
        """Returns int mode of glyph widget """
        return self.glyphWidget.getMode()

    ################################
    # DATA UPDATERS
    def indicatorPanelLabelFormat(self, data):
        """Format data - returns string according to mode selected"""
        if data is not None: pass
        else: return " " # return space as placeholder if no data
        """ Param int Returns str """
        if self.indicatorSelectedLabelMode == 0: return str(data)
        elif self.indicatorSelectedLabelMode == 1: return "0x%02X" % data
        elif self.indicatorSelectedLabelMode == 2:
            controlCharacters = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL", "BS", "HT", "LF", "VT", "FF", "CR", "SO", "SI", "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB", "CAN", "EM", "SUB", "ESC", "FS", "GS", "RS", "US"]
            if data < 32: return controlCharacters[data]
            else: return chr(data).decode(self.indicatorPanelEncodings[self.selectedIndicatorPanelEncoding]["name"], "replace") # 

    def updateSelectedGlyph(self):
        """UPDATES SLECTED GLYPH IN BOTH TEXTFIELD AND PARSED DATA"""
        completeGlyphList = self.processing.getCompleteGlyphList()
        selectedGlyphIndex = self.processing.getSelectedGlyphIndex()

        if len(completeGlyphList) > 0:
            # need at least one glyph
            pass
        else:
            # if no glyphs on list - nothing to update
            return

        self.debugInfo("\n\n================================= DATA UPDATE START =======================================")

        showPosition = completeGlyphList[selectedGlyphIndex][0]["start"] # move textfield cursor to first byte of selected glyph

        self.ignoreTextEvent = True
        for byteindex in range(0,len(completeGlyphList[selectedGlyphIndex])):
            if len(completeGlyphList) > 0:
                tempDict = completeGlyphList[selectedGlyphIndex][byteindex]
            else: break
            startpos = tempDict["start"]
            endpos = tempDict["end"]
            data = self.glyphWidget.data[byteindex]
            self.debugInfo("ui", "UPDATE DATA > startpos", startpos, "> endpos", endpos, "> data", data, "> base 16 > 0x%02X" % (data)) # 
            self.processing.updateCurrentDataset(startpos, endpos, data)
            # Simple method - no colours
            if self.textCtrlModes[self.selectedTextCtrlMode]["method"] == 0: self.updateTextCtrlDataSmart(startpos, endpos, data)

        if self.textCtrlModes[self.selectedTextCtrlMode]["method"] == 1:
            self.textCtrl.ChangeValue(self.processing.getCompleteString())
            #self.textCtrl.ShowPosition(0) # move to start, append leaves cursor at the end
            self.textCtrl.ShowPosition(self.processing.startOffset + showPosition) # move to selected position + add offset

        elif self.textCtrlModes[self.selectedTextCtrlMode]["method"] == 2:
            self.recreateTextfieldFromCurrentData()
            #self.textCtrl.ShowPosition(0) # move to start, append leaves cursor at the end
            self.textCtrl.ShowPosition(self.processing.startOffset + showPosition) # move to selected position + add offset

        self.debugInfo("====================================== DATA UPDATE END ===================================\n\n")
        self.ignoreTextEvent = False

    # FASTEST - most preferred way
    def updateTextCtrlDataSmart(self, startpos, endpos, data):
        """Fastest method, -> newline chars must be fixed before"""
        textfieldStartpos = startpos + self.processing.startOffset
        textfieldEndpos = endpos + self.processing.startOffset
        
        word_colour = wx.TextAttr(wx.RED, wx.LIGHT_GREY) # optional bg: wx.NullColour
        self.textCtrl.Replace(textfieldStartpos, textfieldEndpos, "0x%02X" % (data))
        self.textCtrl.SetStyle(textfieldStartpos, textfieldEndpos, word_colour)

    # OPTIONAL Super SLOW - most featured
    def recreateTextfieldFromCurrentData(self):
        """Fully recreates the textfield, every single value can have its colour depending on state -> using two states, futureproof"""
        self.textCtrl.SetValue("")
        self.textCtrl.SetDefaultStyle(wx.TextAttr(wx.NullColour))
        self.textCtrl.AppendText(self.processing.getStartText()) # append data from start of textfield up to the beginning of parsedText which is startOffset
        peviousEnd = 0
        completeGlyphList = self.processing.getCompleteGlyphList() # 
        for glyph in completeGlyphList:
          for glyphData in glyph:
            startpos = glyphData.get('start')
            endpos = glyphData.get('end')
            text =  (glyphData.get('hexdata'))
            self.textCtrl.AppendText(self.processing.parsedText[peviousEnd:startpos])# append start of textfield - before the hex values
            peviousEnd = endpos

            # Select colour by item state
            style = wx.TextAttr(wx.NullColour)
            state =  (glyphData.get('state'))
            if state == "inserted":
                style = wx.TextAttr(wx.BLUE) # wx.NullColour
            elif state == "modified":
                style = wx.TextAttr(wx.RED, wx.LIGHT_GREY) # 

            self.textCtrl.SetDefaultStyle(style)
            self.textCtrl.AppendText(text)
            self.textCtrl.SetDefaultStyle(wx.TextAttr(wx.NullColour))
        
        self.textCtrl.AppendText(self.processing.parsedText[peviousEnd:]) # append rest of string
        self.textCtrl.AppendText(self.processing.getEndText()) # append rest of textfield

    ################################
    # WIDGET IMAGE DATA LOADERS
    def loadGlyphWidgetImageData(self):
        if not self.processing.glyphList:
            self.debugInfo("ui", "Warning:", "self.processing.glyphList is empty!")
            pass # return
        else:
            self.glyphWidget.data = [ int(sub['hexdata'], 16) for sub in self.processing.glyphList[self.processing.getSelectedGlyphIndex()] ]
            self.debugInfo("ui", "info:", "self.glyphWidget.data loaded with >", self.glyphWidget.data) #

    def loadFontWidgetImageData(self):
        if not self.processing.glyphList:
            self.debugInfo("ui", "Warning:", "self.processing.glyphList is empty!")
            pass # return
        else:
            self.fontWidget.data = [ int(sub['hexdata'], 16) for glyph in self.processing.glyphList for sub in glyph ]
            self.debugInfo("ui", "info:", "self.fontWidget.data loaded with >", len(self.fontWidget.data), "items.") #

    ################################
    # MISC. OTHER
    def getBasePath(self):
        """Returns str path to launch script"""
        return os.path.dirname(os.path.realpath(__file__)) # return dir containing this file

    def debugInfo(self, *text):
        """Prints debug messages to stdout"""
        if DEBUG:
            if self.platform != "__WXMSW__":
                # COLOURS NOT WORKING ON WINDOWS 7
                if ("Event") in text : self.printToStdout("\033[1;32;1m", "\033[0m", *text) # highlight event
                elif ("info:") in text : self.printToStdout("\033[1;34;1m", "\033[0m", *text) # highlight messgae
                elif ("Error") in text : self.printToStdout("\033[1;31;1m", "\033[0m", *text) # highlight error
                elif ("Warning:") in text : self.printToStdout("\033[1;31;1m", "\033[0m", *text) # highlight error
                else: self.printToStdout("", "", *text) # other info
            else:
                self.printToStdout("", "", *text) # no colours available

    def printToStdout(self, header, footer, *text):
        """Replaces print"""
        sys.stdout.write(header)
        for string in text:
            #all to string
            if not isinstance(string, str):
                try:
                    string = str(string)
                except: pass
            try:
                sys.stdout.write(string + " ")
            except: pass
        sys.stdout.write(footer + "\n")

################################################################
# MAIN , wx.App
def main():
    app = wx.App()
    window = MainFrame(None)
    window.Show()
    if DEBUG and showInspectionWindow: wx.lib.inspection.InspectionTool().Show() # DEBUG
    app.MainLoop()

if __name__ == '__main__':
    main()
################################################################
