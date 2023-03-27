#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore, uic
import qt_composite_objects as qtc
import os

class VisWidgetBase( qtw.QWidget ):
    addButtonPressed = QtCore.pyqtSignal( str )
    itemChangedText = QtCore.pyqtSignal( str )
    
    def addButtonWithText( self ):
        self.addButtonPressed.emit( self.getItem() )
        
    def itemChanged( self ):
        self.itemChangedText.emit( self.getItem() )
        
    def fillSelector( self, str_list ):
        self.clearSelector()
        for name in str_list:
            self.act_selector.addItem( name )
    
    
    def findItem( self, name ):
        return self.act_selector.findText( name )
    
    
    def markItem( self, name ):
        self.act_selector.setIcon( self.findItem( name ), self.style().standardIcon(getattr(qtw.QStyle, "SP_DialogApplyButton" ) ))
        
        
    def getItem( self ):
        return self.act_selector.currentText()
    
        
    def clearSelector( self ):
        self.act_selector.clear()
        
        
    def addItem( self, lbl ):
        self.act_selector.addItem( lbl )




class VolumeVisWidget( VisWidgetBase ):
    delButtonPressed = QtCore.pyqtSignal( str )
        
    def __init__( self, parent=None ):
        super().__init__( parent )
        path = os.path.dirname(__file__)
        uic.loadUi( os.path.join( path +"/vol_widget.ui" ), self )
        self.initUI()
        self.act_add.pressed.connect( self.addButtonWithText )
        self.act_del.pressed.connect( self.delButtonWithText )
        self.act_selector.currentIndexChanged.connect( self.itemChanged )
        
        
    def initUI( self ):
        self.act_selector = self.findChild( qtw.QComboBox, "combo_crt_vol_switch" )
        self.act_add = self.findChild( qtw.QPushButton, "act_add_btn" )
        self.act_del = self.findChild( qtw.QPushButton, "act_del_btn" )
        self.bck_clr = qtc.BoxDouble3D.create( self, "back_clr_r", "back_clr_g", "back_clr_b" )
        self.act_vis = self.findChild( qtw.QCheckBox, "box_vis" )
        self.act_fore = self.findChild( qtw.QCheckBox, "box_fore" )
        self.act_clr = qtc.BoxDouble3D.create( self, "act_clr_r", "act_clr_g", "act_clr_b" )
        self.act_opac = qtc.SliderBox.create( self, "slider_opac", "box_opac" )
        self.act_thresh = qtc.SliderBox.create( self, "slider_thresh", "box_thresh" )
        self.thresh_lbl = self.findChild( qtw.QLabel, "thresh_lbl" )
   
        
    def delButtonWithText( self ):
        self.delButtonPressed.emit( self.getItem() )
         
        
    def connectAddButton( self, func ):
        self.act_add.clicked.connect( func )
        
        
    def connectChanceBox( self, func ):
        self.act_selector.currentIndexChanged.connect( func )
        
        
    def connectBackColor( self, func ):
        self.bck_clr.valueChanged.connect( func )
        
        
    def connectActVis( self, func ):
        self.act_vis.stateChanged.connect( func )
        
        
    def connectActFore( self, func ):
        self.act_fore.stateChanged.connect( func )
        
        
    def connectActColor( self, func ):
        self.act_clr.valueChanged.connect( func )
        
        
    def connectActOpac( self, func ):
        self.act_opac.valueChanged.connect( func )
        
        
    def connectActThresh( self, func ):
        self.act_thresh.valueChanged.connect( func )
        
        
    def changeThreshLabel( self, bl ):
        if not bl: 
            self.thresh_lbl.setText( "Thresh" )
        else: self.thresh_lbl.setText( "LineWidth" )
        
        
    def fillFromParams( self, vis, clr, opac, thresh, fore ):
        self.act_vis.setChecked( vis )
        self.act_clr.setValue( clr )
        self.act_opac.setValue( opac )
        self.act_thresh.setValue( thresh )
        self.act_fore.setChecked( fore )
        
        

class SliceVisWidget( VisWidgetBase ):    
    def __init__( self, parent=None ):
        super().__init__( parent )
        path = os.path.dirname(__file__)
        uic.loadUi( os.path.join( path +"/slice_widget.ui" ), self )
        self.initUI()
        self.act_use.pressed.connect( self.addButtonWithText )
        self.act_selector.currentIndexChanged.connect( self.itemChanged )
        
    def initUI( self ):
        self.act_selector = self.findChild( qtw.QComboBox, "combo_crt_vol_switch" )
        self.act_use = self.findChild( qtw.QPushButton, "act_btn" )
        self.bck_clr = qtc.BoxDouble3D.create( self, "back_clr_r", "back_clr_g", "back_clr_b" )
        self.act_thresh = qtc.SliderBox.create( self, "slider_thresh", "box_thresh" )


    def connectActThresh( self, func ):
        self.act_thresh.valueChanged.connect( func )
        
