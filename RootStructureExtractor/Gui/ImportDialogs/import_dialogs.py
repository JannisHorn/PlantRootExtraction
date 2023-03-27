#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
import import_dts as dts
import np_utils
import os

class ImportDialogBase( qtw.QDialog ):
    def __init__( self, parent ):
        super().__init__( parent )
        self.valid = False
        
    def loadUI( self, fname ):
        file_path = os.path.dirname(__file__)
        uic.loadUi( os.path.join( file_path, fname ), self )
        self.button_box = self.findChild( qtw.QDialogButtonBox, "buttons" )
        self.button_box.accepted.connect( self.eventOkPress )
        self.button_box.rejected.connect( self.eventQuit )
        
    def eventOkPress( self ):
        raise RuntimeError( "Error: eventOkPress needs to be reimplemented!" )
        
    def eventQuit( self ):
        self.close()
        
    @classmethod
    def openDialog( dia, parent ):
        dialog = dia( parent )
        dialog.exec_()
        if dialog.valid:
            return dialog.cfg
        else:
            return None    


class ImportRawDialog( ImportDialogBase ):
    def __init__( self, parent ):
        super().__init__( parent )
        self.cfg = dts.RawData()
        self.loadUI( "import_raw.ui" )
        self.initUI()
        
    def initUI( self ):
        self.dt = self.findChild( qtw.QComboBox, "box_dt" )
        self.x = self.findChild( qtw.QSpinBox, "box_x" )
        self.y = self.findChild( qtw.QSpinBox, "box_y" )
        self.z = self.findChild( qtw.QSpinBox, "box_z" )
        self.little_end = self.findChild( qtw.QCheckBox, "box_le" )
        self.swap_axis = self.findChild( qtw.QCheckBox, "box_sa" )
        
    def eventOkPress( self ):
        self.cfg.dt = np_utils.strToNumpyDt( self.dt.currentText() )
        self.cfg.shape = ( self.x.value(), self.y.value(), self.z.value() )
        self.cfg.swap_byte_order = self.little_end.isChecked()
        self.cfg.swap_axis = self.swap_axis.isChecked()
        self.valid = True
        self.close()
        
        
        
class ImportTifDialog( ImportDialogBase ):
    def __init__( self, parent ):
        super().__init__( parent )
        self.cfg = dts.TifData()
        self.loadUI( "import_tif.ui" )
        self.initUI()
        
    def initUI( self ):
        self.res_fac = self.findChild( qtw.QDoubleSpinBox, "box_rescale" )
        
    def eventOkPress( self ):
        self.cfg.rescale_fac = self.res_fac.value()
        self.valid = True
        self.close()
