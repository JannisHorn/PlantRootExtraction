#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import vtk
import vtk_renderer_wrapper as vtk_ren
import vtk_actor_pipe as vtk_act
import time

def LutFromRange( rmin, rmax ):
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(rmin, rmax)
    lut.SetHueRange(0,0.7)
    lut.SetSaturationRange(1,1)
    lut.SetValueRange(1,1)
    lut.SetNanColor( 0,0,0,0 )
    lut.Build()
    return lut

def CreateLutFromData( data ):
    extrs = data.GetPointData().GetArray(0).GetValueRange()
    return LutFromRange( extrs[0], extrs[1] )



class vtkRenderWindowWrapper:
    def __init__( self, win ):
        self.window = win
        
        
    def Clear( self ):
        for rend in self.window.GetRenderers():
            self.window.RemoveRenderer( rend )
        
        
    def Render( self ):
        self.window.Render()
        
        
    def SetAsActive( self ):
        self.Clear()
        self.AddRenderers()
        
        
    def GetInteractor( self ):
        return self.window.GetInteractor()
        
    

class vtkVolumeWindow( vtkRenderWindowWrapper ):
    
    def __init__( self, win ):
        super().__init__( win )
        self.picker = vtk.vtkPointPicker()
        self.foreground = vtk_ren.vtkRendererWrapper( self.picker, self.GetInteractor() )
        self.foreground.SetLayer(1)
        self.renderer = vtk_ren.vtkRendererWrapper( self.picker, self.GetInteractor() )
        self.renderer.SetBackground( 0.4,0.4,0.4 )
        self.renderer.SetLayer(0)
        self.foreground.SetActiveCamera( self.renderer.GetActiveCamera() ) 
        self.has_master = False
        self.st_pt = None
        self.SetStPt( (0,0,0) )
        self.window.SetNumberOfLayers( 2 )
        self.corners = []
        
        
    def AddActor( self, actor ):
        if not self.has_master:
            self.AddMasterActor( actor )
            self.has_master = True
            self.AddCornerPoints()
        else:
            self.AddSlaveActor( actor )
        
        
    def RemoveActor( self, actor ):
        self.renderer.RemoveActor( actor )
        
        
    def Reset( self ):
        self.st_pt = None
        self.SetStPt((0,0,0))
        if self.has_master:
            self.renderer.RemoveActor( self.outline_actor )
            del self.outline_actor
            del self.outline_mapper
            del self.outline
            self.has_master = False
        for actor in self.renderer.GetActors():
            self.RemoveActor( actor )
    

    def SetStPt( self, st_pt, rad = 1 ):
        if self.st_pt is None:
            self.st_pt = vtk_act.vtkSphereActorPipe()
            self.renderer.AddActor( self.st_pt )
            self.st_pt.SetColor( 0.5,1.0,0.5 )
            self.ToForeground( self.st_pt, True )
        self.st_pt.setPos( st_pt[0], st_pt[1], st_pt[2] )
        self.st_pt.setRadius( rad )
        self.Render()
    
            
    def AddCornerPoints( self ):
        if self.has_master:
            for corner in self.corners: 
                self.renderer.RemoveActor( corner )
            self.corners = []
            size = self.master.GetInput().GetDimensions()
            size = (size[2], size[1], size[0])
            corners = [(0,0,0), (0,0,size[2]), (0,size[1],0), (size[0],0,0),
                       (0,size[1],size[2]), (size[0],0,size[2]), (size[0], (size[1]), 0),
                       size]
            for corner in corners:
                vtk_corner = vtk_act.vtkSphereActorPipe()
                self.renderer.AddActor( vtk_corner )
                vtk_corner.setPos( corner[0],corner[1],corner[2] )          
                vtk_corner.setRadius( 0 )
                self.ToForeground( vtk_corner, True )
        
        
    def AddMasterActor( self, actor ):
        print( "vtk: Adding Master Actor" )
        self.master = actor
        self.outline = vtk.vtkOutlineFilter()
        self.outline.SetInputData( actor.GetInput() )
        self.outline_mapper = vtk.vtkPolyDataMapper()
        self.outline_mapper.SetInputConnection( self.outline.GetOutputPort() )
        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper( self.outline_mapper )
        self.outline.Update()
        self.renderer.AddActor( actor )
        self.renderer.AddActor( self.outline_actor )
        self.renderer.SetInteractive( True )
        self.renderer.ResetCamera()
        self.cam = self.renderer.GetActiveCamera()
        
    
    def AddSlaveActor( self, actor ):
        self.renderer.AddActor( actor )
    
    
    def ToForeground( self, actor, to_foreground ):
        if to_foreground and not actor.is_foreground:
            self.renderer.RemoveActor( actor )
            self.foreground.AddActor( actor )
            actor.is_foreground = True
        elif not to_foreground and actor.is_foreground:
            self.foreground.RemoveActor( actor )
            self.renderer.AddActor( actor )
            actor.is_foreground = False
    
    
    def GetOutlineProperty( self ):
        return self.outline_actor.GetProperty()
    
    
    def AddRenderers( self ):
        self.window.AddRenderer( self.renderer )
        self.window.AddRenderer( self.foreground )
    
    
    def Clear( self ):
        super().Clear()
        self.has_master = False
        
    
    
class vtkVolumeSliceWindow( vtkRenderWindowWrapper ):
    
    def __init__( self, win ):
        def initColorFilter():
            self.lut = LutFromRange( 0,1 )
            self.rgb_data = vtk.vtkImageMapToColors()
            self.rgb_data.SetLookupTable( self.lut )
            self.rgb_data.SetInputData( vtk.vtkImageData() )
            self.rgb_data.Update()
        
        def initSliceRenderer( r_min, r_max ):
            renderer = vtk_ren.vtkImageSliceRenderer( self.picker, self.GetInteractor() )
            self.window.AddRenderer( renderer )
            renderer.SetViewport( r_min[0], r_min[1], r_max[0], r_max[1] )
            self.slice_rens.append( renderer )
            
        super().__init__( win )
        initColorFilter()
        self.picker = vtk.vtkPointPicker()
        self.vol_renderer = vtk_ren.vtkRendererWrapper( self.picker, self.GetInteractor() )
        self.vol_renderer.SetBackground( 0.4,0.4,0.4 )
        self.vol_renderer.SetViewport( 0, .5, .5, 1 )
        self.slice_rens = []
        initSliceRenderer( (.5,.5), (1,1) )
        initSliceRenderer( (0,0), (.5,.5) )
        initSliceRenderer( (.5,0), (1,.5) )
        self.vol_renderer.AddActor( self.slice_rens[0].GetPlane() )
        self.vol_renderer.AddActor( self.slice_rens[1].GetPlane() )
        self.vol_renderer.AddActor( self.slice_rens[2].GetPlane() )
        self.current_actor = None 
            
            
    def SetLut( self, lut ):
        self.lut = lut
        self.rgb_data.SetLookupTable( self.lut )
        self.rgb_data.Update()
        self.slice_rens[0].SetLut( self.lut )
        self.slice_rens[1].SetLut( self.lut )
        self.slice_rens[2].SetLut( self.lut )
            
        
    def Reset( self ):
        if self.current_actor is not None:
            self.vol_renderer.RemoveActor( self.current_actor )
        
            
    def AddActor( self, actor, create_lut = True ):
        if self.current_actor is not None:
            self.vol_renderer.RemoveActor( self.current_actor )
        inp = actor.GetInput()
        if( create_lut ):
            self.SetLut( CreateLutFromData( inp ) )
        self.current_actor = actor
        self.current_actor.SetOpacity( 0.9 )
        self.vol_renderer.AddActor( actor )
        self.rgb_data.SetInputData( inp )
        self.slice_rens[0].Init( self.rgb_data, 0, self.lut )
        self.slice_rens[1].Init( self.rgb_data, 1, self.lut )
        self.slice_rens[2].Init( self.rgb_data, 2, self.lut )
        self.vol_renderer.ResetCamera()
        self.SetInter()
        
        
    def RemoveActor( self, actor ):
        self.vol_renderer.RemoveActor( actor )
        
        
    def SetInter( self ):
        inter = self.GetInteractor()
        self.slice_rens[0].SetParent( inter )
        self.slice_rens[1].SetParent( inter )
        self.slice_rens[2].SetParent( inter )
        
        
    def Update( self ):
        self.SetLut( CreateLutFromData( self.current_actor.GetInput() ) )
        
        
    def AddRenderers( self ):
        self.window.AddRenderer( self.vol_renderer )
        self.window.AddRenderer( self.slice_rens[0] )
        self.window.AddRenderer( self.slice_rens[1] )
        self.window.AddRenderer( self.slice_rens[2] )
        
