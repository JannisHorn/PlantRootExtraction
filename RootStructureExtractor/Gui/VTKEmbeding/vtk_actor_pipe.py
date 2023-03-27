#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import vtk

class vtkActorPipeBase( vtk.vtkActor ):

    def __init__( self ):
        def mapperInit():
            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.ScalarVisibilityOff()
                    
        super().__init__()
        mapperInit()
        self.SetMapper( self.mapper )
        self.is_foreground = False
        
    
    def SetColor( self, r, g, b ):
        self.GetProperty().SetColor( r,g,b )
        self.Modified()
        
    def SetOpacity( self, opac ):
        self.GetProperty().SetOpacity( opac )
        self.Modified()
        
        
    def GetParams( self ):
        return [self.GetVisibility(), self.GetProperty().GetColor(), self.GetProperty().GetOpacity(), self.is_foreground]
        
        
    def GetNewActorInstance( self ):
        act = vtk.vtkActor()
        act.SetMapper( self.mapper )
        return act


    def IsForeground( self ):
        return self.is_foreground
    

    def Update( self ):
        self.mapper.Update()



class vtkImageActorPipe( vtkActorPipeBase ):
    
    def __init__( self ):
        def surfaceInit( num_of_isos ):
            self.surface = vtk.vtkFlyingEdges3D()
            self.surface.ComputeNormalsOn()
                
        def thresholdInit():
            self.threshold = vtk.vtkImageThreshold()
            self.threshold.ThresholdByLower( 0.0 )
            self.threshold.SetInValue( 0.0 )
            self.threshold.ReplaceInOn()
            
        super().__init__()
        surfaceInit( 5 )
        thresholdInit()
        self.threshold.SetInputData( vtk.vtkImageData() )
        self.surface.SetInputConnection( self.threshold.GetOutputPort() )
        self.mapper.SetInputConnection( self.surface.GetOutputPort() )
        self.SetMapper( self.mapper )
        
        
    def SetInputData( self, data, num_of_isos=3 ):
        self.threshold.SetInputData( data )
        extrs = data.GetPointData().GetArray(0).GetValueRange()
        self.max = extrs[1]
        self.surface.GenerateValues( num_of_isos, extrs[0], extrs[1] )
        self.surface.Update()
        
        
    def SetThreshold( self, thresh ):
        self.threshold.ThresholdByLower( thresh*self.max )
        self.surface.Update()
        
    
    def GetInput( self ):
        return self.threshold.GetInput()
    
    
    def GetParams( self ):
        return super().GetParams() +[self.threshold.GetUpperThreshold()]
        
        
        
        
class vtkGraphActorPipe( vtkActorPipeBase ):
    
    def __init__( self ):
        super().__init__()
        self.SetInputData( vtk.vtkPolyData() )
        
    
    def SetInputData( self, data ):
        self.mapper.SetInputData( data )
        
        
    def SetLineWidth( self, width ):
        self.GetProperty().SetLineWidth( width )
        
        
    def GetInput( self ):
        return self.mapper.GetInputData()
    
    
    def GetParams( self ):
        return super().GetParams() +[self.GetProperty().GetLineWidth()]
    
    
    
class vtkSphereActorPipe( vtkActorPipeBase ):
    
    def __init__( self ):
        super().__init__()
        self.reset()
        self.SetMapper( self.mapper )
        self.mapper.Update()
        self.active = False
        
        
    def reset( self ):
        self.data = vtk.vtkSphereSource()
        self.mapper.SetInputConnection( self.data.GetOutputPort() )
        
        
    def resetData( self, x,y,z, rad=1.0 ):
        self.data.SetCenter( z,y,x )
        self.data.SetRadius( rad )
        self.mapper.Update()


    def setPos( self, x, y, z ):
        self.data.SetCenter( z,y,x )
        self.data.Update()

    def getPos( self ):
        return self.data.GetCenter()


    def setRadius( self, rad ):
        self.data.SetRadius( rad )
        self.data.Update()
        
    def getRadius( self ):
        return self.data.GetRadius()
