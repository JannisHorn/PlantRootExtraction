#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal
import qt_composite_objects as qtc
import math

class ExtractionWidget( qtw.QWidget ):
    recom_sphere = pyqtSignal()
    recom_cost = pyqtSignal()
    recom_path = pyqtSignal()
    recom_volume = pyqtSignal()
    
    def __init__( self, parent, name ):
        super().__init__( parent )
        self.initExtrCrt( parent )
        self.initNonPrimary()
        
    def initExtrCrt( self, parent ):
        def initVolumeSphereCrt( parent ):
            self.extr_sph_occ_box = qtc.SliderBox.create( parent, "slider_extr_occ", "box_extr_occ" ) 
            self.extr_sph_occ_box.valueChanged.connect( self.recom_sphere )
            self.extr_sph_rad = parent.findChild( qtw.QSpinBox, "box_extr_rad" )
            self.extr_sph_rad.valueChanged.connect( self.recom_sphere )
            
        def initVolumeCostCrt( parent ):
            self.extr_cost_box = qtc.SliderBox.create( parent, "slider_extr_cost", "box_extr_cost" )
            self.extr_cost_box.valueChanged.connect( self.recom_cost )
            self.extr_off_f = parent.findChild( qtw.QSpinBox, "box_extr_off_f" )
            self.extr_off_e = parent.findChild( qtw.QSpinBox, "box_extr_off_e" )
            self.extr_off_f.valueChanged.connect( self.recom_cost )
            self.extr_off_e.valueChanged.connect( self.recom_cost )
            
            #self.extr_sh_idd = parent.findChild( qtw.QSpinBox, "box_extr_idd" )
            #self.extr_sh_idd.valueChanged.connect( self.recom_cost )
            self.extr_sh_cut = parent.findChild( qtw.QDoubleSpinBox, "box_extr_cut" )
            self.extr_sh_cut.valueChanged.connect( self.recom_cost )
            self.extr_sh_min_int = qtc.SliderBox.create( parent, "slider_extr_min_int", "box_extr_min_int" )
            self.extr_sh_min_int.valueChanged.connect( self.recom_cost )
            
            self.extr_button = parent.findChild( qtw.QPushButton, "button_extr" )
            self.extr_button.clicked.connect( parent.eventExtr )
            
        self.extr_gap_closing = parent.findChild( qtw.QCheckBox, "box_gap_closing" )
        self.extr_gap_closing.stateChanged.connect( self.eventGapClosing )
        #self.extr_gap_slider = parent.findChild( qtw.QSlider, "slider_extr_gap_per" )
        #self.extr_gap_slider.valueChanged.connect( self.recom_cost )
        #self.extr_gap_per = qtc.SliderBox.create( parent, "slider_extr_gap_per", "box_extr_gap_per" )
        #self.extr_gap_per.valueChanged.connect( self.recom_cost )
        self.extr_lbl_gap = parent.findChild( qtw.QLabel, "label_extr_gap_per" )
        self.extr_gap_length = parent.findChild( qtw.QSpinBox, "box_extr_gap_len" )
        self.extr_gap_length.valueChanged.connect( self.recom_cost )
        self.extr_lbl_gap_len = parent.findChild( qtw.QLabel, "label_extr_gap_len" )
            
        initVolumeSphereCrt( parent )
        initVolumeCostCrt( parent )

    def initNonPrimary( self ):
        self.non_primary = [self.extr_sph_occ_box,
                            self.extr_sph_rad
                            #self.extr_sh_idd
                            ]
        
        
    def enableNonPrimary( self, enable ):
        for par in self.non_primary:
            par.setEnabled(enable)

    
    def eventGapClosing( self, enb ):
        self.extr_gap_length.setEnabled( enb )
        #self.extr_gap_per.setEnabled( enb )
        #self.extr_gap_slider.setEnabled( enb )
        #self.extr_lbl_gap.setEnabled( enb )
        self.extr_lbl_gap_len.setEnabled( enb )
        self.recom_cost.emit()

    def fillExtrConfig( self, cfg ):
        """ Fill extraction config from GUI elements """
        cfg.sphere_occ = self.extr_sph_occ_box.value()
        cfg.sphere_rad = self.extr_sph_rad.value()
        cfg.cost_w_rad = self.extr_cost_box.value()
        cfg.cost_off = self.extr_off_f.value() *pow( 10, -self.extr_off_e.value() )
        cfg.sh_pt_idd = 3 #self.extr_sh_idd.value()
        cfg.sh_pt_cutoff = self.extr_sh_cut.value()
        cfg.sh_pt_min_int = self.extr_sh_min_int.value()
        cfg.fill_graph = self.extr_gap_closing.isChecked()
        cfg.gap_closing = self.extr_gap_closing.isChecked()
        cfg.gap_per = self.extr_sh_min_int.value()
        cfg.gap_length = self.extr_gap_length.value()

        
    def updateExtr( self, ecfg ):
        def offsetFromVal( val ):
            if val != 0.0:
                log_val = -math.floor( math.log10( val ) ) 
                return round( val *math.pow( 10, log_val ) ), log_val
            else:
                return 0, 0
        
        sphere = ecfg["Sphere"]
        val = sphere["MinOcc"]
        self.extr_sph_occ_box.setValue( val )
        self.extr_sph_rad.setValue( sphere["MaxRad"] )
        self.extr_sh_min_int.setValue( sphere["MinInt"] )
        cost = ecfg["CostFunc"]
        val = cost["RadWeight"]
        self.extr_cost_box.setValue( val )
        val, log_val = offsetFromVal( cost["Offset"] )
        self.extr_off_f.setValue( val )
        self.extr_off_e.setValue( log_val )
        shpt = ecfg["ShortestPath"]
        #self.extr_sh_idd.setValue( shpt["Idd"] )
        self.extr_sh_cut.setValue( shpt["Cutoff"] )
        if "GapClosing" in ecfg:
            gap = ecfg["GapClosing"]
            self.extr_gap_closing.setChecked( True )
            self.extr_gap_length.setValue( int(gap["Length"]) )
        
