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
import re

################################################################
class DataProcessing():
    def __init__(self, mainwindow, fontBytewidth):
        self.mainwindow = mainwindow # main window reference
        self.debug = self.mainwindow.debugInfo # debug info goes to main

        self.startOffset = 0 # offset where the first data begins - most likely inside curly braces
        self.endOffset = 0 # offset of end of parsed data from end of input string

        # DATA
        self.importedText = "" # input from textfield
        self.parsedText = "" # extracted from self.importedText
        self.glyphList = [] # list of dicts extracted from self.parsedText, serves as metadata

        self.fontBytewidth = fontBytewidth # DEFAULT, gets changed whenever data is loaded
        self.selectedGlyphIndex = 0 # index of selected glyph in data or ascii

    ################
    # SETTERS & GETTERS
    def setSelectedGlyphIndex(self, newSelected):
        """Set selected glyph"""
        if newSelected >= len(self.glyphList):
            self.selectedGlyphIndex = 0
        else: self.selectedGlyphIndex = newSelected

    def getSelectedGlyphIndex(self):
        """Returns int selected glyph index"""
        return self.selectedGlyphIndex

    def getFontByteWidth(self):
        """Returns byte width"""
        return self.fontBytewidth

    def getStartText(self):
        """Returns part of input from beginning of input string up to startOffset, including curly brace if present"""
        return self.importedText[:self.startOffset] #

    def getEndText(self):
        """Returns part of input string after parsed area, including curly brace if present"""
        return (self.importedText[-self.endOffset:] if self.endOffset else "") #

    def getCompleteString(self):
        """Returns complete string"""
        self.debug("core", "self.importedText[:self.startOffset]",self.importedText[:self.startOffset])
        self.debug("core", "self.parsedText", self.parsedText)
        self.debug("core", "self.importedText[-self.endOffset:]",self.importedText[-self.endOffset:])
        return self.importedText[:self.startOffset] + self.parsedText + (self.importedText[-self.endOffset:] if self.endOffset else "") # Conditional Expressions require python 2.5 https://docs.python.org/2.5/whatsnew/pep-308.html

    def getCompleteGlyphList(self):
        """Returns list of dicts containing parsed data with offsets in string"""
        return self.glyphList

    def getGlyphCount(self):
        """Returns count of glyphs on list"""
        return len(self.glyphList)

    ################
    # PARSERS
    def importData(self, importedText):
      """Import text to parse"""
      currentInputText = "" #
      self.importedText = importedText #
      inputMatch = re.search(r'(?s)\{(.*?)\}', self.importedText) # search for strings inside curly braces first

      # if found, scan extracted string further for hex values
      if inputMatch:
          currentInputText = inputMatch.group(1)
          # set offsets of extracted string inside input from TextCtrl
          self.startOffset = inputMatch.start(1)
          self.endOffset = len(self.importedText) - inputMatch.end(1)

      else:
          # text field erased completely or not found any hex values in curly braces
          # try to search hex strings in whole input then
          currentInputText = self.importedText
          # set PROPER OFFSETS!
          self.startOffset = 0
          self.endOffset = 0

      # check if currentInputText is list - future - listable sets of fonts
      if isinstance(currentInputText, list):
        try:
          self.parsedText = currentInputText[0] # 
        except IndexError:
          self.parsedText = currentInputText # 
      else:
          self.parsedText =  currentInputText # 

      self.debug("core", "Parse start offset:", self.startOffset)
      self.debug("core", "Parse end offset:", self.endOffset)
      self.debug("core", "self.parsedText:", self.parsedText)

      # detect bytes per glyph
      splitLines = self.parsedText.splitlines()
      occurenceList = []
      for line in splitLines:
          occurences = re.findall('(0x[a-fA-F0-9]{2})', line)
          numOccurences = len(occurences)
          if numOccurences: occurenceList.append(numOccurences)
      self.debug("core", "occurenceList", occurenceList)

      counter = 0
      mostCommon = 0 
      
      for value in occurenceList: 
          currentCount = occurenceList.count(value) 
          if(currentCount> counter): 
              counter = currentCount 
              mostCommon = value 

      self.debug("core", "info:", "Detected", mostCommon, "Bytes per glyph.")
      self.fontBytewidth = mostCommon # byte width set to autodetected -> most common count of Bytes per line of extracted string! ! !

      # finally do a scan on self.parsedText
      self.parseTextToGlyphList()

    def parseTextToGlyphList(self):
        """Parse text"""
        self.currentDataset = [] # dataset is flat list of values
        self.glyphList = [] # values sorted in order to be used along with other gathered parameters like their offsets in string
        #prepare data to be read from the string
        stringsfound = re.sub('(0x[a-fA-F0-9]{2})', self.foundhex ,self.parsedText) #
        # done here, put items found into lists representing single glyph so it can be treated as it
        # if self.fontBytewidth > 0
        if self.fontBytewidth:
            self.glyphList = [self.currentDataset[ i : i + self.fontBytewidth] for i in range(0, len(self.currentDataset), self.fontBytewidth)]
            if self.selectedGlyphIndex >= len(self.glyphList):
                # fix selection index if its beyond new data
                self.debug("core", "Warning:", "Fixed selected index!", "self.selectedGlyphIndex", self.selectedGlyphIndex, "len(self.glyphList)", len(self.glyphList))
                self.selectedGlyphIndex = 0
        self.debug("\n\n\n\nself.glyphList:", self.glyphList, "\n\n\n\nglyphList size:", len(self.glyphList), "\n\n\n\n")

    def foundhex(self, matchobj):
        """Adds hex value to current array of dicts - glyph list"""
        #self.debug("String comin in -->", str(matchobj.group(1)), "start -->", matchobj.start(1), "end -->", matchobj.end(1)) # ULTRA VERBOSE
        #self.debug("String coming at pos -->", matchobj.span(1)) # ULTRA VERBOSE
        tempdict = {}
        tempdict['start'] =  matchobj.start(1)
        tempdict['end'] =  matchobj.end(1)
        tempdict['hexdata'] =  matchobj.group(1)
        tempdict['state'] = "inserted"
        tempdict['line'] = self.parsedText[:matchobj.end(1)].count('\n')
        self.currentDataset.append(tempdict) # append data

        return str(matchobj.group(1))

    ################
    # DATA UPDATERS
    def updateSelectedGlyph(self, data):
        """ """ # TODO add missing description
        pass
        
    def updateCurrentDataset(self, startpos, endpos, data):
        """Updates currently selected glyph in both input and glyphlist"""
        # update raw string
        self.parsedText = self.parsedText[:startpos] + "0x%02X" % (data) + self.parsedText[endpos:]
        # update data in parsed values
        for glyphData in self.glyphList[self.selectedGlyphIndex]:
            if glyphData.get('start') == startpos:
                glyphData.update({'hexdata' : "0x%02X" % (data)})
                glyphData.update({'state' : "modified"})

    ################
    # DATA INSERTERS
    def insertToRight(self):
        """  """
        if not self.parsedText or not self.glyphList:
            # both checks required - parsedText can contain rest of non base 16 data - checking glyphlist empty ensures to avoid this operation
            self.debug("core", "Warning:", "Insert right: no data to insert to!")
            return
        else:
            self.currentInsertionIndex = 0
            newString = re.sub('(0x[a-fA-F0-9]{2})', self.re_insertRight ,self.parsedText) #
            self.fontBytewidth = self.fontBytewidth + 1

            self.parsedText = newString # <--------------------- update input!
            self.parseTextToGlyphList() # <--------------------- scan it!

    def re_insertRight(self, matchobj):
        """  """
        self.currentInsertionIndex = self.currentInsertionIndex + 1
        if self.currentInsertionIndex % self.fontBytewidth == 0:
            return matchobj.group(1) + ", 0x00"
        else: return matchobj.group(1)

    def insertToLeft(self):
        """  """
        if not self.parsedText or not self.glyphList:
            # both checks required - parsedText can contain rest of non base 16 data - checking glyphlist empty ensures to avoid this operation
            self.debug("core", "Warning:", "Insert left: no data to insert to!")
            return
        else:
            self.currentInsertionIndex = 0
            newString = re.sub('(0x[a-fA-F0-9]{2})', self.re_insertLeft , self.parsedText) #
            self.fontBytewidth = self.fontBytewidth + 1

            self.parsedText = newString # <--------------------- update input!
            self.parseTextToGlyphList() # <--------------------- scan it!

    def re_insertLeft(self, matchobj):
        """  """
        if self.currentInsertionIndex % self.fontBytewidth == 0:
            self.currentInsertionIndex = self.currentInsertionIndex + 1
            return "0x00, " + matchobj.group(1)
        else:
            self.currentInsertionIndex = self.currentInsertionIndex + 1
            return matchobj.group(1)

    ################
    # DATA ERASERS
    def eraseFromRight(self):
        """  """
        if not self.parsedText or not self.glyphList:
            # both checks required - parsedText can contain rest of non base 16 data - checking glyphlist empty ensures to avoid this operation
            self.debug("core", "Warning:", "Erase from right: no data to erase!")
            return
        else:
            if self.fontBytewidth > 1:
                # this is floor where we can safely erase - up to zero
                self.currentInsertionIndex = 0
                newString = re.sub('( ?0x[a-fA-F0-9]{2},?)', self.re_eraseRight , self.parsedText) # including space before and comma after
                self.fontBytewidth = self.fontBytewidth - 1
                self.parsedText = newString # <--------------------- update input!
                self.parseTextToGlyphList() # <--------------------- scan it!

    def re_eraseRight(self, matchobj):
        """  """
        self.currentInsertionIndex = self.currentInsertionIndex + 1
        if self.currentInsertionIndex % self.fontBytewidth == 0:
            return ""
        else: return matchobj.group(1)

    def eraseFromLeft(self):
        """  """
        if not self.parsedText or not self.glyphList:
            # both checks required - parsedText can contain rest of non base 16 data - checking glyphlist empty ensures to avoid this operation
            self.debug("core", "Warning:", "Erase from left: no data to erase!")
            return
        else:
            if self.fontBytewidth > 1:
                # this is floor where we can safely erase - up to zero
                self.currentInsertionIndex = 0
                newString = re.sub('( ?0x[a-fA-F0-9]{2},? ?)', self.re_eraseLeft , self.parsedText) # eat right space and comma too
                self.fontBytewidth = self.fontBytewidth - 1 # 
                self.parsedText = newString # <--------------------- update input!
                self.parseTextToGlyphList() # <--------------------- scan it!

    def re_eraseLeft(self, matchobj):
        """  """
        if self.currentInsertionIndex % self.fontBytewidth == 0:
            self.currentInsertionIndex = self.currentInsertionIndex + 1
            return ""
        else:
            self.currentInsertionIndex = self.currentInsertionIndex + 1
            return matchobj.group(1)
################################################################
