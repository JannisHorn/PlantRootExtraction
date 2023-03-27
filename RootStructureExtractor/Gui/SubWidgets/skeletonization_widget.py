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

class SkeletonizationWidget( qtw.QWidget ):
    recom_skel = pyqtSignal()
    recom_int = pyqtSignal()
    
    def __init__( self, parent, name ):
        super().__init__( parent )
        self.initSkeletonCrt( parent )
        self.initNonPrimary()

    def initSkeletonCrt( self, parent ):
        self.skel_use_extr = parent.findChild( qtw.QCheckBox, "skel_use_extr" )
        #self.skel_idd = parent.findChild( qtw.QSpinBox, "box_skel_idd" )
        #self.skel_idd.valueChanged.connect( self.recom_skel )
        self.skel_use_graph = parent.findChild( qtw.QCheckBox, "skel_use_oldg" )
        self.skel_bt_load = parent.findChild( qtw.QPushButton, "button_loadgraph" )
        self.skel_bt_load.clicked.connect( self.recom_skel )
        self.skel_bt_load.clicked.connect( parent.eventLoadOldGraph )
        self.skel_dil_add = parent.findChild( qtw.QSpinBox, "box_skel_add" )
        self.skel_dil_add.valueChanged.connect( self.recom_skel )
        self.skel_cut_dim = parent.findChild( qtw.QComboBox, "cbox_z_cut" )
        self.skel_cut_dim.currentIndexChanged.connect( self.recom_skel )
        self.skel_z_cut = parent.findChild( qtw.QSpinBox, "box_z_cut" )
        self.skel_z_cut.valueChanged.connect( self.recom_skel )
        self.skel_qp_dist = parent.findChild( qtw.QDoubleSpinBox, "box_qp_dist" )
        self.skel_qp_dist.valueChanged.connect( self.recom_skel )
        
        self.skel_lin_int = parent.findChild( qtw.QCheckBox, "check_skel_li" )
        self.skel_lin_int.stateChanged.connect( self.recom_int )
        self.skel_lin_diff = parent.findChild( qtw.QDoubleSpinBox, "box_skel_li_diff" )
        self.skel_lin_diff.valueChanged.connect( self.recom_int )
        self.skel_min_len = parent.findChild( qtw.QDoubleSpinBox, "box_skel_min_len" )
        self.skel_min_len.valueChanged.connect(self.recom_int)
        self.skel_min_rad = parent.findChild( qtw.QDoubleSpinBox, "box_skel_min_rad" )
        self.skel_min_rad.valueChanged.connect(self.recom_int)

        self.skel_button = parent.findChild( qtw.QPushButton, "button_skel" )
        self.skel_button.clicked.connect( parent.eventSkel )
        
    def initNonPrimary( self ):
        self.non_primary = []
        
    def enableNonPrimary( self, enable ):
        for par in self.non_primary:
            par.setEnabled(enable)

    def setUseGraph( self ):
        self.skel_use_graph.setChecked( True )
        
    def fillSkelConfig( self, cfg ):
        """ Fill skeletonization config from GUI elements """
        cfg.idd = 3 #self.skel_idd.value()
        cfg.dil_sum = self.skel_dil_add.value()
        cfg.z_cut = self.skel_z_cut.value()
        cfg.cut_axis = self.skel_cut_dim.currentIndex()
        cfg.lin_int = self.skel_lin_int.isChecked()
        cfg.lin_int_diff = self.skel_lin_diff.value()
        cfg.qp_min_dist = self.skel_qp_dist.value()
        cfg.min_br_length = self.skel_min_len.value()
        cfg.min_br_radius = self.skel_min_rad.value()
        cfg.use_old_graph = self.skel_use_graph.isChecked()
        
    def updateSkel( self, scfg ):
        #self.skel_idd.setValue( scfg["Idd"] )
        self.skel_dil_add.setValue( scfg["Dilation"] )
        self.skel_lin_int.setChecked( scfg["LinInter"] )
        self.skel_lin_diff.setValue( scfg["LinInterDiff"] )
        self.skel_z_cut.setValue( scfg["ZCut"] )
        self.skel_qp_dist.setValue( scfg["QpMinDist"] )
        self.skel_min_len.setValue( scfg["MinBrLength"] )
        self.skel_min_rad.setValue( scfg["MinBrRadius"] )
