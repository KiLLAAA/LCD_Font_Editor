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

import wx

################################################################
class OptionsFrame(wx.Frame):
    def __init__(self, parent, position):
        ################
        # INIT
        wx.Frame.__init__(self, parent, pos= position, size=(160,320), title="Options & Settings") #
        self.SetWindowStyle(style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP) # stay on top itself on win -> no borders
        self.parent = parent

        mainPanel = wx.Panel(self)
        mainPanel.SetBackgroundColour("#4f5049")

        ################
        # Labels
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.optionsLabel = wx.StaticText(mainPanel, label="Options")
        self.optionsLabel.SetForegroundColour("#FFFFFF")
        self.optionsLabel.SetFont(font)
        self.settingsLabel = wx.StaticText(mainPanel, label="Settings")
        self.settingsLabel.SetForegroundColour("#FFFFFF")
        self.settingsLabel.SetFont(font)

        ################
        # INSERTION BUTTONS
        self.addRightButton = wx.Button(mainPanel,id = wx.ID_ANY, label="Insert line to right")
        self.addRightButton.identifier = "insertright"
        self.Bind(wx.EVT_BUTTON, self.onButton, self.addRightButton)

        self.addLeftButton = wx.Button(mainPanel,id = wx.ID_ANY, label="Insert line to left")
        self.addLeftButton.identifier = "insertleft"
        self.Bind(wx.EVT_BUTTON, self.onButton, self.addLeftButton)

        ################
        # REMOVAL BUTTONS
        self.removeRightButton = wx.Button(mainPanel,id = wx.ID_ANY, label="Remove rightmost line")
        self.removeRightButton.identifier = "removeright"
        self.Bind(wx.EVT_BUTTON, self.onButton, self.removeRightButton)

        self.removeLeftButton = wx.Button(mainPanel,id = wx.ID_ANY, label="Remove leftmost line")
        self.removeLeftButton.identifier = "removeleft"
        self.Bind(wx.EVT_BUTTON, self.onButton, self.removeLeftButton)

        ################
        # SELECT GLYPH PANEL MODE COMBOBOX
        glyphPanelModes = [mode['name'] for mode in self.parent.getGlyphWidgetModesAvailable()]
        self.selectGlyphWidgetMode = wx.ComboBox(mainPanel, value = glyphPanelModes[self.parent.getGlyphWidgetMode()], choices=glyphPanelModes, style=wx.CB_READONLY) # 
        self.selectGlyphWidgetMode.Bind(wx.EVT_COMBOBOX, self.onSelectGlyphWidgetMode)
        self.selectGlyphWidgetMode.SetToolTip(wx.ToolTip("Glyph Panel Mode"))

        ################
        # SELECT FONT PANEL MODE COMBOBOX
        fontPanelModes = [mode['name'] for mode in self.parent.getFontWidgetModesAvailable()]
        self.selectFontWidgetMode = wx.ComboBox(mainPanel, value = fontPanelModes[self.parent.getFontWidgetMode()], choices=fontPanelModes, style=wx.CB_READONLY) # 
        self.selectFontWidgetMode.Bind(wx.EVT_COMBOBOX, self.onSelectFontWidgetMode)
        self.selectFontWidgetMode.SetToolTip(wx.ToolTip("Font Panel Mode"))

        ################
        # SELECT TEXTFIELD MODE COMBOBOX
        textCtrlModes = [mode['name'] for mode in self.parent.getTextCtrlModesAvailable()]
        self.selectTextMode = wx.ComboBox(mainPanel, value = textCtrlModes[self.parent.getTextCtrlMode()], choices=textCtrlModes, style=wx.CB_READONLY) # 
        self.selectTextMode.Bind(wx.EVT_COMBOBOX, self.onSelectTextMode)
        self.selectTextMode.SetToolTip(wx.ToolTip("Textfield Mode"))

        ################
        # SELECT ENCODING COMBOBOX
        encodings = [encoding['name'] for encoding in self.parent.getIndicatorPanelEncodingsAvailable()]
        self.selectEncoding = wx.ComboBox(mainPanel, value = encodings[self.parent.selectedIndicatorPanelEncoding], choices=encodings, style=wx.CB_READONLY)
        self.selectEncoding.Bind(wx.EVT_COMBOBOX, self.onSelectEncoding)
        self.selectEncoding.SetToolTip(wx.ToolTip("Indicator Encoding"))

        ################
        # OPTIONS
        sizerOptions = wx.BoxSizer(wx.VERTICAL)
        sizerOptions.Add(self.optionsLabel, 0, wx.ALL |wx.ALIGN_CENTER_HORIZONTAL, 4)
        
        sizerOptions.Add(self.addRightButton, 0, wx.EXPAND | wx.ALL, 20)
        sizerOptions.Add(self.addLeftButton, 0, wx.EXPAND | wx.ALL, 20)
        sizerOptions.Add(self.removeRightButton, 0, wx.EXPAND | wx.ALL, 20)
        sizerOptions.Add(self.removeLeftButton, 0, wx.EXPAND | wx.ALL, 20)

        #self.separator = wx.StaticLine(mainPanel)
        #vbox.Add(self.separator, 0, wx.EXPAND | wx.ALL, 20)
        ####   wx.BOTTOM | wx.TOP | wx.LEFT  |wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL 

        ################
        # SETTINGS
        sizerSettings = wx.BoxSizer(wx.VERTICAL)
        sizerSettings.Add(self.settingsLabel, 0, wx.ALL |wx.ALIGN_CENTER_HORIZONTAL, 4)
        
        sizerSettings.Add(self.selectGlyphWidgetMode, 0, wx.EXPAND | wx.ALL, 20)
        sizerSettings.Add(self.selectFontWidgetMode, 0, wx.EXPAND | wx.ALL, 20)
        sizerSettings.Add(self.selectTextMode, 0, wx.EXPAND | wx.ALL, 20)
        sizerSettings.Add(self.selectEncoding, 0, wx.EXPAND | wx.ALL, 20)

        ################
        # MAIN PANEL SIZER
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(sizerOptions, 0, wx.EXPAND | wx.ALL, 20)
        mainSizer.Add(sizerSettings, 0, wx.EXPAND | wx.ALL, 20)
        
        mainPanel.SetSizer(mainSizer)

        # https://wxpython.org/Phoenix/docs/html/window_sizing_overview.html
        mainSizer.Fit(self) # make sizer resize parent window to best size - https://wxpython.org/Phoenix/docs/html/wx.Sizer.html#wx.Sizer.Fit


    ################
    # EVENTS
    def onButton(self, event):
        """Process button events"""
        self.parent.onButtons(event) # Button events are sent to main ui

    def onSelectEncoding(self, event):
        """Process Indicator Panel encoding combo event"""
        combo = event.GetEventObject()
        encoding = combo.GetCurrentSelection()
        self.parent.setIndicatorPanelLabelsEncoding(encoding)
        
    def onSelectTextMode(self, event):
        """Process TextCtrl mode combo event"""
        #modeIndex = self.selectTextMode.GetCurrentSelection() # old
        combo = event.GetEventObject()
        modeIndex = combo.GetCurrentSelection()
        self.parent.setTextCtrlMode(modeIndex)
        
    def onSelectGlyphWidgetMode(self, event):
        """Process Glyph Widget mode combo event"""
        combo = event.GetEventObject()
        modeIndex = combo.GetCurrentSelection()
        self.parent.setGlyphWidgetMode(modeIndex)
        
    def onSelectFontWidgetMode(self, event):
        """Process Font Widget mode combo event"""
        combo = event.GetEventObject()
        modeIndex = combo.GetCurrentSelection()
        self.parent.setFontWidgetMode(modeIndex)
################################################################
