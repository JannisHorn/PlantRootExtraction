#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore, QtGui

class MenuBar( QtCore.QObject ):
    def __init__( self, parent, name ):
        super().__init__( parent )
        self.initFileMenuBar( parent )
        self.initEditMenuBar( parent )
        
    def initFileMenuBar( self, parent ):
        """ Find File Menu entries and connect them to events """
        self.open = parent.findChild( qtw.QAction, "actionOpen_2" )   
        self.open.triggered.connect( parent.eventOpenFile )
        
        self.open_cfg = parent.findChild( qtw.QAction, "actionOpen_Config" )
        self.open_cfg.triggered.connect( parent.eventOpenCfg )
        self.open_inp = parent.findChild( qtw.QAction, "actionOpen_input_xml" )
        self.open_inp.triggered.connect( parent.eventOpenInput )
        self.open_extr = parent.findChild( qtw.QAction, "actionOpen_extraction_npy" )
        self.open_extr.triggered.connect( parent.eventOpenExtr )
        self.open_skel = parent.findChild( qtw.QAction, "actionOpen_graph_xml" )
        self.open_skel.triggered.connect( parent.eventOpenSkel )
        
        self.save = parent.findChild( qtw.QAction, "actionSave" )
        self.save.triggered.connect( parent.eventSaveFile )
        self.save_as = parent.findChild( qtw.QAction, "actionSave_As" )
        self.save_as.triggered.connect( parent.eventSaveAsFile )
        self.save_graph_as = parent.findChild( qtw.QAction, "actionSave_Graph_As" )
        self.save_graph_as.triggered.connect( parent.eventSaveGraphAsXml )
        
        self.import_raw = parent.findChild( qtw.QAction, "actionImport_raw" )
        self.import_raw.triggered.connect( parent.eventImportRaw )
        
        self.import_tif = parent.findChild( qtw.QAction, "actionImport_tif" )
        self.import_tif.triggered.connect( parent.eventImportTif )
        
        self.quit = parent.findChild( qtw.QAction, "actionQuit" )
        self.quit.triggered.connect( parent.close )
        
    def initEditMenuBar( self, parent ):
        """ Find Edit Menu Elements """
        self.edit_extr_vol = parent.findChild( qtw.QAction, "actionExtract_Volume" )
        self.edit_extr_vol.triggered.connect( parent.eventExtr )
        
        self.edit_extr_skel = parent.findChild( qtw.QAction, "actionExtract_Skeleton" )
        self.edit_extr_skel.triggered.connect( parent.eventSkel )
        
        self.edit_stop = parent.findChild( qtw.QAction, "actionStop_Execution" )
        self.edit_stop.triggered.connect( parent.eventStop )
        
        self.edit_free = parent.findChild( qtw.QAction, "actionFree_Memory" )
        self.edit_free.triggered.connect( parent.eventFreeMem )
        
    def enableFileOps( self, enable ):
        self.open.setEnabled( enable )
        self.open_cfg.setEnabled( enable )
        self.open_extr.setEnabled( enable )
        self.open_inp.setEnabled( enable )
        self.open_skel.setEnabled( enable )
        self.save.setEnabled( enable )
        self.save_as.setEnabled( enable )
        self.import_raw.setEnabled( enable )
        self.import_tif.setEnabled( enable )
        
    def enableEditOps( self, enable ):
        self.edit_extr_vol.setEnabled( enable )
        self.edit_extr_skel.setEnabled( enable )
        self.edit_stop.setEnabled( not enable )
