#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import sys
from PyQt5 import QtWidgets, uic

class Window(QtWidgets.QMainWindow):
    def __init__( self ):
        super( Window, self ).__init__()
        uic.loadUi( "Gui/gui.ui", self )
        self.show()
        
app = QtWidgets.QApplication(sys.argv)
win = Window()
sys.exit(app.exec_())
