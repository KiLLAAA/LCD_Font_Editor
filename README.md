# LCD Font Editor
![Image of LCD Font Editor](https://raw.githubusercontent.com/KiLLAAA/LCD_Font_Editor/master/images/lcdfonteditor.gif)

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

Written by Lukas Vyhnalek aka KiLLA.<br/>
BSD license, read LICENSE for more information.<br/>
All text above must be included in any redistribution.<br/>

### DESCRIPTION
Graphic editor of hard-coded fonts for LCD and OLED displays.

### FEATURES

---

- first graphic editor of hard-coded fonts ever
- works DIRECTLY with text in real time
- written in Python
- autodetects font width
- modifies font width
- compare with glyphs with various encodings
- development status - production/stable
- operating system independent (to some extent)
- designed to rely on as few external modules as possible
- requires only one third-party python module - wxPython
- hand coded GUI with custom widgets, no generator used
- recommended cpu: Phenom II or faster

| Operating System | Installation methods | State |
| --- | --- | --- |
| Linux | setuptools, pip | Tested |
| Windows | pip | Tested |
| macOS | pip | TODO: Test |

### LIMITATIONS

---

- NO open/save file feature present - this software works DIRECTLY with text data pasted into its text field
- install wxPython manually on Windows - this is to avoid problems with pip not detecting wxPython installed by .exe installer after requirement in metadata was found
- Windows entry in start menu or desktop is left up to user for now (create .lnk to eg. "C:\Python27\python.exe lcdfonteditor" opened in "C:\Python27\Scripts\")
- macOS entry in start menu or desktop is left up to user

### TODO

---

- optimize font display widget draw area
- autosave settings
- add option to select colours to Options window
- Undo/Redo mechanism
- Windows entry in start menu or desktop - create bat file to make .lnk without another dependency
- FAR future: variable font height, horizontal data mode
- future considerations: move to numpy, move to GTK, port co c++
