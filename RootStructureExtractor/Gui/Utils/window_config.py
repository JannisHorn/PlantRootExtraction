#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5.QtCore import QSettings, QSize, QPoint

class WindowConfig( QSettings ):
    
    def __init__( self ):
        super().__init__( QSettings.IniFormat, QSettings.UserScope, "Uni Bonn", "RootStructureExtractor" )
        
        
    def fillFromWindow( self, win ):
        self.beginGroup( "MainWindow" )
        self.setValue( "pos", win.pos() )
        self.setValue( "size", win.size() )
        self.setValue( "fullscreen", win.isMaximized() )
        self.setValue( "splitter", win.main_splitter.saveState() )
        self.endGroup()
        
        self.beginGroup( "CrtPanel" )
        self.setValue( "splitter", win.crt_splitter.saveState() )
        self.setValue( "id", win.crt_tbox.currentIndex() )
        self.endGroup()
        
        self.setValue( "LastData/path", win.data.getPath() )
        
        
    def windowFromSettings( self, win, no_data ):
        self.beginGroup( "MainWindow" )
        win.resize( self.value( "size", QSize( 1280, 869 ) ) )
        win.move( self.value( "pos", QPoint( 0,0 ) ) )
        sfsc = self.value( "fullscreen", "False" )
        if sfsc == "False": win.showMaximized()
        split = self.value( "splitter" )
        if split is not None: win.main_splitter.restoreState( split )
        self.endGroup()
        
        self.beginGroup( "CrtPanel" )
        split = self.value( "splitter" )
        if split is not None: win.crt_splitter.restoreState( split )
        win.crt_tbox.setCurrentIndex( int( self.value( "id", 0 ) ) )
        self.endGroup()
        
        if not no_data:
            fname = self.value( "LastData/path", "" )
            if not fname == "":
                try:
                    print( "Loading old data: {0}".format( fname ) )
                    win.data.load( fname )
                    win.data_tree.updateTreeView( win.data )
                    win.updateWindowFromCfgs( win.data.getStatus().items )
                    win.updateVtk( ["Input", "Extraction", "Graph"], True )
                    win.cur_path = fname
                    print( "Loading {0} complete".format( fname ) )
                except IOError as e:
                    self.errorDialog( "Loading Error: {0}".format( e ) )
