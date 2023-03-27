#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QObject, pyqtSignal

class Shortcut( qtw.QShortcut ):
    def __init__( self, parent, sequence_str, cmd ):
        super().__init__( QKeySequence( sequence_str ), parent )
        self.activated.connect( cmd )
        self.setEnabled( True )


class SliderBox( QObject ):
    valueChanged = pyqtSignal( float )
    
    @classmethod
    def create( cls, widg, slider_name, box_name ):
        slider = widg.findChild( qtw.QSlider, slider_name )
        box = widg.findChild( qtw.QDoubleSpinBox, box_name )
        return cls( slider, box, widg )
        
    def __init__( self, slider, box, parent=None ):
        super().__init__( parent )
        self.slider = slider
        self.box = box
        self.slider.valueChanged.connect( self._sliderToBox )
        self.box.valueChanged.connect( self._boxToSlider )
        self.valueChanged.connect( self.box.valueChanged )
        
    def _sliderToBox( self, val ):
        n_val = val/100
        self.box.setValue( n_val )
        self.valueChanged.emit( n_val )
        
    def _boxToSlider( self, val ):
        self.slider.setValue( val*100 )
        
    def value( self ):
        return self.box.value()
    
    def setValue( self, val ):
        self.slider.setValue( val*100 )
        self.box.setValue( val )
        
    def setEnabled( self, enable ):
        self.slider.setEnabled( enable )
        self.box.setEnabled( enable )
        
        
        
class Box3DBase( QObject ):
    def __init__( self, box0, box1, box2, parent=None ):
        super().__init__( parent )
        self.boxes = [box0, box1, box2]
        self.boxes[0].valueChanged.connect( self._captureValueChange )
        self.boxes[1].valueChanged.connect( self._captureValueChange )
        self.boxes[2].valueChanged.connect( self._captureValueChange )
                
    def _captureValueChange( self, i ):
        self.valueChanged.emit( self.boxes[0].value(), self.boxes[1].value(), self.boxes[2].value() )
        
    def getValue( self ):
        return self.boxes[0].getValue(), self.boxes[1].getValue(), self.boxes[2].getValue()
    
    def setValue( self, pt ):
        self.boxes[0].setValue( pt[0] )
        self.boxes[1].setValue( pt[1] )
        self.boxes[2].setValue( pt[2] )
    
class Box3D( Box3DBase ):
    valueChanged = pyqtSignal( int, int, int )
    
    @classmethod
    def create( cls, widg, box0_name, box1_name, box2_name ):
        box0 = widg.findChild( qtw.QSpinBox, box0_name )
        box1 = widg.findChild( qtw.QSpinBox, box1_name )
        box2 = widg.findChild( qtw.QSpinBox, box2_name )
        return cls( box0, box1, box2, widg )
    
    def __init__( self, box0, box1, box2, parent=None ):
        super().__init__( box0, box1, box2, parent )
        
class BoxDouble3D( Box3DBase ):
    valueChanged = pyqtSignal( float, float, float )
    
    @classmethod
    def create( cls, widg, box0_name, box1_name, box2_name ):
        box0 = widg.findChild( qtw.QDoubleSpinBox, box0_name )
        box1 = widg.findChild( qtw.QDoubleSpinBox, box1_name )
        box2 = widg.findChild( qtw.QDoubleSpinBox, box2_name )
        return cls( box0, box1, box2, widg )
    
    def __init__( self, box0, box1, box2, parent=None ):
        super().__init__( box0, box1, box2, parent )
        
