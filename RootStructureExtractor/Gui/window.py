#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""



import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
import ImportDialogs as imp_dia
import multi_threading
import window_config as w_cfg
import qt_composite_objects as qtc
import menu_bar, data_tree, extraction_widget, skeletonization_widget, visualization
import numpy as np

import PyUtils.data_wrapper as dh

class REGui( qtw.QMainWindow ):
    """ Root Extraction GUI. Using PyQt5 and VTK """
    
    #Init Window
    def __init__( self, tp_path, no_settings, no_data ):
        super().__init__()
        self.initEnvironment()
        self.initUI()
        self.setTempPath( tp_path +"temp_graph.xml" )
        self.cfg = w_cfg.WindowConfig()
        self.cur_path = ""
        if not no_settings: self.cfg.windowFromSettings( self, no_data )
        print( "Window instantiated" )
        
        
    
    def initEnvironment( self ):
        """ Init path variables and booleans """
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.data_saved = True
        self.data = dh.DataWrapper()
        self.worker = multi_threading.AlgorithmController()
        self.worker.started.connect( self.lockExecution )
        self.worker.finished.connect( self.unlockExecution )
        self.worker.error.connect( self.threadError )
    
    def initAlgoThread( self ):
        self.algo_thread = multi_threading.Algorithm()
            
    def initUI( self ):
        """ Control function calling all segment init functions """
        uic.loadUi( self.path +"/gui.ui", self )
        self.menu = menu_bar.MenuBar( self, "menubar" )
        self.initControlUI()
        self.show()
        self.vis_crt.initRenderer()
    

    def initControlUI( self ):
        """ Init control field """
        def connectExtr():
            self.extr_crt.recom_sphere.connect( self.extrRecomSphere )
            self.extr_crt.recom_cost.connect( self.extrRecomCost )
            self.extr_crt.recom_path.connect( self.extrRecomPath )
            self.extr_crt.recom_volume.connect( self.extrRecomVolume )
            self.extr_crt.enableNonPrimary( False )
        def connectSkel():
            self.skel_crt.recom_int.connect( self.eventSkelChangedInt )
            self.skel_crt.recom_skel.connect( self.eventSkelChangedSkel )
            self.skel_crt.enableNonPrimary( False )
        
        self.initDatasetCrt()
        self.main_splitter = self.findChild( qtw.QSplitter, "splitter_main" )
        self.crt_splitter = self.findChild( qtw.QSplitter, "splitter_crt" )
        self.crt_tbox = self.findChild( qtw.QToolBox, "tabs_control" )
        self.extr_crt = extraction_widget.ExtractionWidget( self, "page_vis_control_inner" )
        connectExtr()
        self.skel_crt = skeletonization_widget.SkeletonizationWidget( self, "page_skelet"   )
        self.vis_crt = visualization.VisWidget( self, "page_vis_scroll_inner", self.data )
        self.data_tree = data_tree.DataTreeWidget( self, "tree_view_elems" )
        self.statusbar = self.findChild( qtw.QStatusBar, "statusbar" )
        self.ready()
        
    def initDatasetCrt( self ):
        self.st_pt = qtc.Box3D.create( self, "box_dt_st_pt_x", "box_dt_st_pt_y", "box_dt_st_pt_z" )
        self.st_pt.valueChanged.connect( self.eventStPt )
        
        self.dm_x = self.findChild( qtw.QDoubleSpinBox, "box_dt_dm_x" )
        self.dm_x.valueChanged.connect( self.eventDmX )
        self.dm_y = self.findChild( qtw.QDoubleSpinBox, "box_dt_dm_y" )
        self.dm_y.valueChanged.connect( self.eventDmY )
        self.dm_z = self.findChild( qtw.QDoubleSpinBox, "box_dt_dm_z" )
        self.dm_z.valueChanged.connect( self.eventDmZ )
        self.bt_find_stpt = self.findChild( qtw.QPushButton, "button_find_stpt" )
        self.bt_find_stpt.clicked.connect( self.eventFindStPt )
        
        self.min_age = self.findChild( qtw.QSpinBox, "box_dt_min_age" )
        self.min_age.valueChanged.connect( self.eventMinAge )
        self.max_age = self.findChild( qtw.QSpinBox, "box_dt_max_age" )
        self.max_age.valueChanged.connect( self.eventMaxAge )
        self.max_type = self.findChild( qtw.QSpinBox, "box_dt_max_type" )
        self.max_type.valueChanged.connect( self.eventMaxType )
        self.vox_res = self.findChild( qtw.QDoubleSpinBox, "box_dt_vox_res" )
        self.vox_res.valueChanged.connect( self.eventVoxRes )

        

    #----- FileHandling Events -----    
    def eventOpenFile( self ):
        """ File Menu -> Open Event -> Calls underlining data_wrapper """
        try:
            self.status( "Loading" )
            fname = qtw.QFileDialog.getOpenFileName( self, "Open Input File", self.cur_path, "Numpy Files (*.npy *.npz)" )[0]
            if fname != "":
                self.data.load( fname )
                self.data_tree.updateTreeView( self.data )
                self.updateWindowFromCfgs( self.data.getStatus().items )
                self.updateVtk( ["Input", "Extraction", "Graph"], True )
        except IOError as e:
            self.errorDialog( "Loading Error: {0}".format( e ) )
        finally:
            self.ready()
            
    def eventOpen( self, data_func, dia_str ):
        try:
            self.status( "Loading" )
            fname = qtw.QFileDialog.getOpenFileName( self, dia_str, self.cur_path )[0]
            if fname != "":
                data_func( fname )
                self.data_tree.updateTreeView( self.data )
                self.updateWindowFromCfgs( self.data.getStatus().items )
                self.updateVtk()
        except IOError as e:
            self.errorDialog( "Loading Error: {0}".format( e ) )
        finally:
            self.ready()
            
    def eventOpenInput( self ):
        self.eventOpen( self.data.loadInput, "Open Input File" )
    def eventOpenCfg( self ):
        self.eventOpen( self.data.loadCfg, "Open Config File" )
    def eventOpenExtr( self ):
        self.eventOpen( self.data.loadExtr, "Open Extraction File" )
    def eventOpenSkel( self ):
        self.eventOpen( self.data.loadSkel, "Open Graph File" )
        
    def eventSaveFile( self ):     
        """ File Menu -> Save Event -> Calls underlining data_wrapper """
        if not self.data.validFile():
            self.eventSaveAsFile()
        else:
            self.status( "Saving" )
            self.data.save()
            self.data_tree.updateTreeView( self.data )
            self.status( "Ready" )

    def eventSaveAsFile( self ):
        """ File Menu -> Save As Event -> Calls underlining data_wrapper """
        try:
            sfname = qtw.QFileDialog.getSaveFileName( self, "Save File to" )[0]
            self.status( "Saving" )
            self.data.save( sfname )
        except IOError as e:
            self.errorDialog( "Error while saving: {0}".format( e ) )
        finally:
            self.ready()

    def eventSaveGraphAsXml( self ):
        """ File Menu -> Save Graph As Event """
        try:
            gfname = qtw.QFileDialog.getSaveFileName( self, "Save Graph as xml to" )[0]
            self.status( "Saving" )
            self.data.saveGraph( gfname )
        except IOError as e:
            self.errorDialog( "Error while saving: {0}".format( e ) )
        finally:
            self.ready()

    def eventImportRaw( self ):
        try:
            self.status( "Loading" )
            fname = qtw.QFileDialog.getOpenFileName( self, "Import .raw File", self.cur_path, "Raw file (*.raw)" )[0]
            if fname != "":
                cfg = imp_dia.ImportRawDialog.openDialog( self )
                if cfg is not None:
                    self.data.importInput( fname, cfg )
                    self.data_tree.updateTreeView( self.data )
                    self.updateWindowFromCfgs( self.data.getStatus().items )
                    self.updateVtk()
        except IOError as e:
            self.errorDialog( "Loading Error: {0}".format( e ) )
        finally:
            self.ready()
            
            
    def eventImportTif( self ):
        try:
            self.status( "Loading" )
            fname = qtw.QFileDialog.getOpenFileName( self, "Import .tif Stack", self.cur_path, "Tiff file (*.tif)" )[0]
            if fname != "":
                cfg = imp_dia.ImportTifDialog.openDialog( self )
                if cfg is not None:
                    self.data.importInput( fname, cfg )
                    self.data_tree.updateTreeView( self.data )
                    self.updateWindowFromCfgs( self.data.getStatus().items )
                    self.updateVtk()
        except IOError as e:
            self.errorDialog( "Import .tif Error: {0}".format( e ) )
        finally:
            self.ready()
    
    
  #----- Edit File Menu Event -----
    def eventStop( self ):
        print( "Terminating execution" )
        self.worker.stop()
        
        
    def eventFreeMem( self ):
        print( "Freeing intermidiate Memory" )
        self.data.extr.freeIntermidiateData()

    
  #----- Dataset Panel Events -----
    def eventStPt( self, x, y, z ):
        self.data.cfg.st_pt = np.array([x,y,z], dtype=np.int32)
        self.vis_crt.vtk_widg.SetStPt( (x,y,z) )
        if self.data.skel.old_graph is not None:
            self.data.skel.old_graph.translateTo( self.data.cfg.st_pt.astype( np.float64 ) )
            self.vis_crt.UpdateDatapoint( "Old Graph" )

        
    def eventDmX( self, i ): 
        self.data.cfg.dim_mults[0] = i
    def eventDmY( self, i ): 
        self.data.cfg.dim_mults[1] = i
    def eventDmZ( self, i ): 
        self.data.cfg.dim_mults[2] = i
        
    def eventMinAge( self, i ):
        self.data.cfg.ages[0] = int(i)
    def eventMaxAge( self, i ):
        self.data.cfg.ages[1] = int(i)
        
    def eventMaxType( self, i ):
        self.data.cfg.max_type = int(i)
        
    def eventVoxRes( self, d ):
        self.data.cfg.vox_res = float(d)
        self.data.data.modified = [False, True]
        
    def eventFindStPt( self ):
        print("Find st_pt")
        depth = self.data.cfg.st_pt[0]
        x,y = self.data.findStartPoint( depth )
        print("x:{}, y:{}".format(x,y))
        self.st_pt.setValue( (depth, x, y) )
    
    
  #----- Extraction Panel Events -----
    def extrRecomSphere( self ): self.data.extr.recom_sphere = True
    def extrRecomCost( self ): self.data.extr.recom_cost = True
    def extrRecomPath( self ): self.data.extr.recom_path = True
    def extrRecomVolume( self ): self.data.extr.recom_volume = True
  
    def eventExtr( self ):           
        """ Handle extraction button event
        Fill config and call data wrapper if input is valid
        Call GUI updates
        """
        if self.data.valid():
            self.extr_crt.fillExtrConfig( self.data.extr.cfg )
            self.status( "Computing Volume Extraction" )
            self.executeAlgorithm( self.data.extractVolume )
        else:
            self.errorDialog( "No input data loaded" )
        
            
  #----- Skeletonization Panel Events -----
    def eventSkelChangedSkel( self ): self.data.skel.recom_skel = True   
    def eventSkelChangedInt( self ): self.data.skel.recom_int = True

    def eventLoadOldGraph( self ):
        """
        Load old graph and add to skeletonization controller
        :return: None
        """
        try:
            fname = qtw.QFileDialog.getOpenFileName(self, "Load graph .xml", self.cur_path, "Xml graph (*.xml *.npy *.npz)")[0]
            graph = self.data.file.loadGraph( fname )
            self.data.skel.old_graph = graph
            self.skel_crt.setUseGraph()
            self.updateVtk()
        except IOError as e:
            self.errorDialog(str(e))

    def eventSkel( self ):
        """ Handle skeletonize button event
        Fill config and call data wrapper
        Call GUI updates
        """
        if self.data.valid():
            self.skel_crt.fillSkelConfig( self.data.skel.cfg )
            try:
                if self.skel_use_extr.isChecked():
                    self.status( "Computing Skeleton" )
                    self.executeAlgorithm( self.data.extractSkeleton, True )
                else:
                    self.status( "Computing Skeleton" )
                    self.executeAlgorithm( self.data.extractSkeleton, False )
            except IOError as e:
                self.errorDialog( str(e) )
        else:
            self.errorDialog( "No input data loaded" )
    
    
  #----- Update Visualization -----
    def updateWindowFromCfgs( self, cfg ):
        """ Get config dictionary and update GUI elements """
        def updateData( dcfg ):
            try:
                self.st_pt.setValue( dcfg["StartPos"] )
                self.dm_x.setValue( dcfg["DimMults"][0] )
                self.dm_y.setValue( dcfg["DimMults"][1] )
                self.dm_z.setValue( dcfg["DimMults"][2] )
                self.min_age.setValue( int( dcfg["MinAge"] ) )
                self.max_age.setValue( int( dcfg["MaxAge"] ) )
                self.max_type.setValue( int( dcfg["MaxType"] ) )
                self.vox_res.setValue( float( dcfg["VoxelRes"] ) )
            except KeyError as e:
                print( "Missing key: {0}".format( e ) )
        
        if "Input" in cfg: updateData( cfg["Input"] )
        if "Extraction" in cfg: self.extr_crt.updateExtr( cfg["Extraction"] )
        if "Skeletonization" in cfg: self.skel_crt.updateSkel( cfg["Skeletonization"] )
    
    def updateVtk( self, data_names=list(), reset=False ):
        print("Updating vtk")
        if self.data.valid():
            self.vis_crt.Update( self.data.getKeys(), data_names, reset )

    
  #----- Control Window Status -----
    def enableExecution( self, enable ):
        self.extr_crt.extr_button.setEnabled( enable )
        self.skel_crt.skel_button.setEnabled( enable )

    def executeAlgorithm( self, func, *args ):
        self.worker.setFunction( func, *args )
        self.worker.start()
   
    def lockExecution( self ):
        self.enableExecution( False )
        self.menu.enableFileOps( False )
        self.menu.enableEditOps( False )
        
    def unlockExecution( self ):
        self.enableExecution( True )
        self.menu.enableFileOps( True )
        self.menu.enableEditOps( True )
        self.data_tree.updateTreeView( self.data )
        self.updateVtk()
        self.ready()
        
    def threadError( self, err ):
        self.errorDialog( err )
        self.enableExecution( True )
        self.menu.enableFileOps( True )
        self.menu.enableEditOps( True )
        self.ready()
    
    def status( self, msg ):
        self.statusbar.showMessage( msg )
    
    def ready( self ):
        self.statusbar.showMessage( "Ready" )
    
    def errorDialog( self, msg ):
        error_msg = qtw.QMessageBox()
        error_msg.setWindowTitle( "Error" )
        error_msg.setIcon( qtw.QMessageBox.Critical )
        error_msg.setText( msg )
        error_msg.exec_()
        self.ready()
        
    def closeEvent( self, event ):
        self.cfg.fillFromWindow( self )
        if not self.data_saved:
            qs_close = qtw.QMessageBox.question( self, "Unsaved Changes", "Unsaved changes will be lost! Continue?", 
                                                 qtw.QMessageBox.Yes | qtw.QMessageBox.No, 
                                                 qtw.QMessageBox.No)
            if qs_close == qtw.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore() 
                
    def setTempPath( self, temp_path ):
        self.data.extr.temp_graph = temp_path
        self.data.skel.temp_graph = temp_path
