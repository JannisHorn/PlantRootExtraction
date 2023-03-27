#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore, QtGui
import VTKEmbeding as vtk_emb
import qt_composite_objects as qtc
import QtVisWidgets as qt_wins

""" 
TODO: 
-Allow to pick and enhance areas
-Write custom keyboard-based interactor 
"""

class VisWidget( QtCore.QObject ):    
    def __init__( self, parent, name, dt_ctr ):
        super().__init__( parent )
        self.initVTKWidget( parent, dt_ctr )
        self.initVisualizationCrt( parent )
        self.has_input = False
        self.has_extraction = False
        self.has_graph = False
        self.has_old_graph = False
        
        
    def initVisualizationCrt( self, parent ):
        self.volume_widg = qt_wins.vis_widget.VolumeVisWidget()
        self.slice_widg = qt_wins.vis_widget.SliceVisWidget()
        self.vis_crt = parent.findChild( qtw.QScrollArea, "vis_crt_scroll_area" )
        self.vis_crt_layout = qtw.QVBoxLayout()
        self.vis_crt_layout.setContentsMargins( 0,0,0,0 )
        self.vis_crt.widget().setLayout( self.vis_crt_layout )
        
        self.vis_selector = parent.findChild( qtw.QComboBox, "vis_crt_win_box" )
        self.vis_selector.insertItem( 0, "Volume View" )
        self.vis_selector.insertItem( 1, "Slice View" )
        self.vis_selector_shortcut_0 = qtc.Shortcut( parent, "Ctrl+1", self.changeToVolWidg )
        self.vis_selector_shortcut_1 = qtc.Shortcut( parent, "Ctrl+2", self.changeToSplitWidg )
        self.vis_selector.currentIndexChanged.connect( self.viewSelectorChanged )
        self.vis_selector.setCurrentIndex( 0 )
        
        self.vis_selector.currentIndexChanged.connect( self.changeCrtWidget )
        self.vis_selector.currentIndexChanged.connect( self.vtk_widg.SetActiveWindow )
        self.vis_crt_layout.addWidget( self.volume_widg )
        self.vis_crt_layout.addWidget( self.slice_widg )
        self.slice_widg.setVisible(False)
        self.active_crt_widg = self.volume_widg
        self.vtk_widg.ConnectToVolCrtWidget( self.volume_widg )
        self.vtk_widg.ConnectToSliceCrtWidget( self.slice_widg )
        
        
    def initVTKWidget( self, parent, dt_ctr ):
        self.vtk_frame = parent.findChild( qtw.QFrame, "frame_visualize" )
        self.vtk_lay = qtw.QVBoxLayout()
        self.vtk_lay.setContentsMargins(0,0,0,0)
        self.vtk_widg = vtk_emb.vtkWindowInteractor( self.vtk_frame, dt_ctr )
        self.vtk_lay.addWidget(self.vtk_widg)
        self.vtk_frame.setLayout(self.vtk_lay)
        
        
    def changeToVolWidg( self ): self.vis_selector.setCurrentIndex( 0 )
    def changeToSplitWidg( self ): self.vis_selector.setCurrentIndex( 1 )
        
    def changeCrtWidget( self, it ):
        if it == 0:
            self.setCrtWidget( self.volume_widg )
        elif it == 1:
            self.setCrtWidget( self.slice_widg )
    
    def setCrtWidget( self, widg ):
        self.active_crt_widg.setVisible( False )
        widg.setVisible( True )
        self.active_crt_widg = widg
        
        
    def fromKeys( self ):
        keys = self.vtk_widg.data.GetKeys() 
        self.volume_widg.fillSelector( keys )
        self.slice_widg.fillSelector( self.vtk_widg.data.GetImageKeys() )
    
        
    def initRenderer( self ):
        self.vtk_widg.Initialize()
        
        
    def viewSelectorChanged( self, idx ):
        self.vis_crt_layout.removeWidget( self.volume_widg )
        if idx == 0:
            self.vis_crt_layout.addWidget( self.volume_widg )
        elif idx == 1:
            pass
    
    
    def SetStPt( self, pos ):
        pass
    

    def FillData( self, data ):
        print(data)
        for key in data:
            if key in ["Graph", "Old Graph"]:
                self.vtk_widg.data.SetPolyData( key )
            else:
                self.vtk_widg.data.SetImageData( key )
        print(self.vtk_widg.data.im_data)

    
    def Update( self, data, data_name, reset ): 
        if reset: 
            self.vtk_widg.Clear()
            self.FillData( data )
        else: 
            self.FillData( data )
            self.UpdateDefaultView()
            self.vtk_widg.Update()
        self.fromKeys()
        if reset:
            self.Default()

    def UpdateDatapoint( self, key ):
        if key in ["Graph", "Old Graph"]:
            self.vtk_widg.data.SetPolyData(key)
        else:
            self.vtk_widg.data.SetImageData(key)


    def UpdateDefaultView( self ):
        if not self.has_input: self.DefaultInput()
        if not self.has_extraction: self.DefaultExtraction()
        if not self.has_graph: self.DefaultGraph()
        if not self.has_old_graph: self.DefaultOldGraph()
        
    def Default( self ):
        self.has_input = False
        self.has_extraction = False
        self.has_graph = False
        self.has_old_graph = False
        self.vis_selector.setCurrentIndex( 0 )
        self.vtk_widg.SetActiveWindow(0)
        self.DefaultInput()
        self.DefaultExtraction()
        self.DefaultGraph()

    def DefaultInput( self ):
        self.has_input = True
        self.vtk_widg.AddActor( "Input" )
        self.vtk_widg.SetActorParams( "Input", (1,1,1), 0.5 )

    def DefaultExtraction( self ):
        self.has_extraction = True
        self.vtk_widg.AddActor( "Extraction" )
        self.vtk_widg.SetActorParams( "Extraction", (1,.3,.3), .7 )

    def DefaultGraph( self ):
        self.has_graph = True
        self.vtk_widg.AddActor( "Graph" )
        self.vtk_widg.SetActorParams( "Graph", (.5,.5,1), 1 )

    def DefaultOldGraph( self ):
        self.has_old_graph = True
        self.vtk_widg.AddActor("Old Graph")
        self.vtk_widg.SetActorParams("Old Graph", (.25, .25, .25), 1)
