#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

"""
TODO: 
- get n-largest clusters in top layer as starting points
- allow for multiple extracted segments in a single scan      
"""

import os
import sys

import Algorithm
import PyUtils
import arg_parser

def guiMode( temp_path, args ):
    from PyQt5 import QtWidgets as qtw
    from PyQt5.QtCore import QLocale
    from Gui import window
    
    loc = QLocale( QLocale.C )
    QLocale.setDefault( loc )           # Change C localization to en for number conversions
    app = qtw.QApplication(sys.argv)
    win = window.REGui( temp_path, args.no_settings, args.no_data )
    win.setLocale( QLocale('English') ) # Change Qt localization to en for , -> .
    sys.exit(app.exec_())


def tempFolder():
    path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir( path +"/Temp" ):
        os.mkdir( path +"/Temp" )
    temp_path = path +"/Temp/"
    return temp_path

def main():
    sys.setrecursionlimit(25000)        # Graph construction from c-graph can exceed default recursionlimit
    parser = arg_parser.ArgParser()
    args = parser.parse()
    if args.recompile:
        Algorithm.forceRecompile()
    #temp_folder = tempFolder()         # temp folder to store temp volumes currently not needed
    temp_folder = ""
    guiMode( temp_folder, args )
    

if __name__ == "__main__":
    main()
