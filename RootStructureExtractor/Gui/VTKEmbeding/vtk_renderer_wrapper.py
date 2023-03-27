#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import vtk
import vtk_custom_interactor as vtk_ci

class vtkRendererWrapper( vtk.vtkRenderer ):
    def __init__( self, picker, parent ):
        super().__init__()
        self.interactor = vtk_ci.vtkInteractorTrackballPicker( picker, parent )
        self.interactor.SetRenderer( self )
        self.point = None
        
        
    def GetInteractorStyle( self ):
        return self.interactor
    
    
    def SetPoint( self, point ):
        if point is not None:
            self.point = [point[0], point[1], point[2]]
            print("Volume Point: [{:.1f}, {:.1f}, {:.1f}]".format(self.point[0], self.point[1], self.point[2]))
        
        
        

class vtkImageSliceRenderer( vtk.vtkRenderer ):
    def __init__( self, picker, parent ):
        super().__init__()
        self.mapper = vtk.vtkImageSliceMapper()
        self.mapper.SetInputData( vtk.vtkImageData() )
        self.actor = vtk.vtkImageSlice()
        self.bar_actor = vtk.vtkScalarBarActor()
        self.text_actor = vtk.vtkTextActor()
        self.plane_act = vtk.vtkActor()
        
        self.interactor = vtk_ci.vtkInteractorStyleImageSlice( picker, parent )
        
        self.actor.SetMapper( self.mapper )
        self.AddActor( self.actor )
        self.AddActor( self.bar_actor )
        self.AddActor( self.text_actor )
        self.point = None
        
        
    def InitMapper( self, dim ):
        self.mapper.SetOrientation(dim)
        self.dim = dim
        self.slice = 0
        self.bounds = ( self.mapper.GetSliceNumberMinValue(), self.mapper.GetSliceNumberMaxValue() )
        
    
    def InitImageSlice( self ):
        self.actor.SetPosition( 0,0,0 )
        props = vtk.vtkImageProperty()
        props.SetInterpolationTypeToNearest()
        self.actor.SetProperty( props )
        self.new_pos = [0,0,0]
        
        
    def InitPlane( self, dim, size ):
        self.plane_source = vtk.vtkPlaneSource()
        pts = [ [size[0],0,0], [0,size[1],0], [0,0,size[2]] ]
        self.plane_pts = [[0,0,0]] +pts[:dim] +pts[dim+1:]
        self.MovePlane(0)
    
        plane_mapper = vtk.vtkPolyDataMapper()
        plane_mapper.SetInputData( self.plane_source.GetOutput() )
        self.plane_act.SetMapper( plane_mapper )
        self.plane_act.GetProperty().SetColor( 1.0, 0.2, 0.2 )
        self.plane_act.GetProperty().SetOpacity( 0.35 )
        
        
    def InitBar( self, lut ):
        self.bar_actor.SetTitle( "Intensity" )
        self.bar_actor.SetNumberOfLabels(5)
        self.bar_actor.SetLookupTable( lut )
        
        
    def InitText( self ):
        self.text_actor.SetInput( "{0}/{1}".format( 0, self.size[self.dim]-1 ) )
        self.text_actor.SetPosition2( 40,20 )
        self.text_actor.GetTextProperty().SetFontSize( 24 )
    
    
    def InitCamera( self, size ):
        center = [int(size[0]/2), int(size[1]/2), int(size[2]/2)]
        self.focal_point = [center[0]-1,center[1],center[2]]
        self.cam_pos = center
        self.focal_point[self.dim] = 0
        cam_height = max( size[0], size[1], size[2] )
        self.cam_pos[self.dim] = -cam_height*1.8
        self.ResetCamera()
    
        
    def ResetCamera( self ):
        cam = vtk.vtkCamera()
        cam.SetPosition(self.cam_pos)    
        cam.SetFocalPoint(self.focal_point)
        self.SetActiveCamera(cam)
        #self.RenderCall()
    
    
    def Init( self, inp, dim, lut ):
        self.dim = dim
        self.SetInputConnection( inp )
        self.InitMapper( dim )
        self.InitImageSlice()
        self.InitPlane( dim, self.size )
        self.InitBar( lut )
        self.InitText()
        self.interactor.SetRenderer( self )
        self.InitCamera( self.size )
        #self.SetBackground( 0.4, 0.4, 0.4 )
    
        
    def SetInputConnection( self, inp ):
        self.mapper.SetInputConnection( inp.GetOutputPort() )
        self.size = inp.GetInput().GetDimensions()
        
        
    def SetLut( self, lut ):
        self.bar_actor.SetLookupTable( lut )
        self.bar_actor.Modified()
        
        
    def SetParent( self, parent ):
        self.interactor.parent = parent
        
      
    def MovePlane( self, coor_dim ):
        self.plane_pts[0][self.dim] = coor_dim
        self.plane_pts[1][self.dim] = coor_dim
        self.plane_pts[2][self.dim] = coor_dim
        self.plane_source.SetOrigin( self.plane_pts[0] )
        self.plane_source.SetPoint1( self.plane_pts[1] )
        self.plane_source.SetPoint2( self.plane_pts[2] )
        self.plane_source.Update()
        
        
    def GetPlane( self ):
        return self.plane_act
        
        
    def GetInteractorStyle( self ):
        return self.interactor
        
        
    def ChangeSlice( self, sl_it ):
        if sl_it < self.bounds[0]:
            sl_it = self.bounds[0]
        elif sl_it > self.bounds[1]:
            sl_it = self.bounds[1]
        self.mapper.SetSliceNumber( sl_it )
        self.slice = sl_it
        self.new_pos[self.dim] = -sl_it
        self.actor.SetPosition(self.new_pos)
        self.text_actor.SetInput( "{0}/{1}".format( self.slice, self.size[self.dim]-1 ) )
        self.MovePlane( sl_it )
        self.mapper.Update()
        self.RenderCall()
      
    def IncrementSlice( self ):
        self.ChangeSlice( self.slice +1 )
        
    def DecrementSlice( self ):
        self.ChangeSlice( self.slice -1 )
        
        
    def SetPoint( self, point ):
        self.point = [point[0], point[1], point[2]]
        self.point[self.dim] = self.slice
        print( "Selected Point: {0}".format( self.point ) )
        
        
    def RenderCall( self ):
        self.interactor.parent.GetRenderWindow().Render()
