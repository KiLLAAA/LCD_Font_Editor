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

import setuptools

################################################################
######################### SETUP SCRIPT #########################

sys.stdout.write("Setuptools version: %s \n" % str(setuptools.__version__)) #
sys.stdout.write("Python version: %s \n" % str(sys.version)) #

################
# PLATFORM SPECIFIC
LINUX = sys.platform.startswith('linux')
MAC = sys.platform.startswith('darwin')
WINDOWS = sys.platform.startswith('win')

if LINUX:
    # install requirements
    requirements = ["wxPython"]
    # menu entry
    os_files = [("share/applications", ["linux/lcdfonteditor.desktop"])]
elif MAC:
    requirements = ["wxPython"]
    os_files = None # no other platform specific files
elif WINDOWS:
    requirements = None # drop requirement of wxPython as it makes offline installation fail on Windows with wxPython installed via exe file
    os_files = None # no other platform specific files

################
# SETUP
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lcd-font-editor",
    version="1.2.1",
    author="Lukas Vyhnalek aka KiLLA",
    author_email="killa dot czech at gmail dot com",
    description="Graphic editor of hard-coded fonts for LCD and OLED displays.",
    license="BSD-2-Clause",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KiLLAAA/",
    packages=["lcdfonteditor", "lcdfonteditor.ui", "lcdfonteditor.ui.dataprocessing"],
    package_data={"lcdfonteditor.ui": ["icons/*.png"]},
    data_files=os_files,
    python_requires='>=2.6',
    scripts=["bin/lcdfonteditor"],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Embedded Systems',
    ],
)

################
# POST-INSTALL
desktop_file_content = """[Desktop Entry]
Comment=Graphic editor of hard-coded fonts for LCD and OLED displays
Comment[cs]=Grafický editor napevno zakódovaných fontů pro LCD a OLED displeje
Terminal=false
Name=LCD Font Editor
Name[cs]=LCD Font Editor
Exec=lcdfonteditor
Type=Application
Icon=fonts
Categories=Development;Graphics;
GenericName=Edit hard-coded fonts
"""

if LINUX:
    # possible file locations
    desktop_file_path = os.path.join(sys.prefix, "share/applications", "lcdfonteditor.desktop")
    desktop_file_path_local = os.path.join(sys.prefix, "local/share/applications", "lcdfonteditor.desktop")

    # check if desktop file was installed by setup
    if os.path.isfile(desktop_file_path):
        # menu entry already exists
        sys.stdout.write("Menu entry is in %s\n" % desktop_file_path) # 
    elif os.path.isfile(desktop_file_path_local):
        # menu entry already exists
        sys.stdout.write("Menu entry is in %s\n" % desktop_file_path_local) # 
    else:
        # if not found in above locations create file even if pip or setuptools will not be aware of it
        with open(desktop_file_path, "w") as fh:
            fh.write(desktop_file_content)
            sys.stdout.write("Menu entry created in %s\n" % desktop_file_path)
else: sys.stdout.write("Creating menu entry is currently supported for linux only.\n")
################################################################
