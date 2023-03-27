#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import vtk
from vtk.util import numpy_support
             
class vtkDataCollection:
    def __init__( self, source ):
        self.source = source
        self.im_data = dict()
        self.poly_data = dict()
        self.misc_data = dict()
        
    
    def SetImageData( self, name ):
        if name in self.im_data:
            if self.im_data[name] is not None:
                array = self.source.getData( name )   
                vtkUpdateImage( self.im_data[name], array )
        else:
            self.im_data[name] = None
    
    def GetImageData( self, name ):
        if self.im_data[name] is not None: return self.im_data[name]
        array = self.source.getData( name )                    
        self.im_data[name] = vtkNumpyToVtkImage( array )
        print( "Getting image {} from {}".format( name, self.im_data ) )
        return self.im_data[name]
    
    def DeleteImageData( self, name ):
        del self.im_data[name]
        self.im_data[name] = None
        
    def GetImageKeys( self ):
        return self.im_data.keys()
    
        
    
    def SetPolyData( self, name ):
        print( self.poly_data )
        graph = self.source.getData( name )
        if name in self.poly_data:
            print( "   Update PolyData" )
            self.poly_data[name] = vtkFromGraph( graph, self.poly_data[name] )
        else:
            print( "   Use new PolyData" )
            self.poly_data[name] = vtkFromGraph( graph )
            
    
    def GetPolyData( self, name ):
        return self.poly_data[name]
    
    def GetPolyDataKeys( self ):
        return self.poly_data.keys()
        
        
    def SetStPtData( self, pos ):
        self.misc_data["st_pt"] = vtkSphereFromParams( pos, 1 )
        
    def GetStPt( self ):
        return self.misc_data["st_pt"]
    
    
    def GetKeys( self ):
        return list( self.im_data.keys() ) +list( self.poly_data.keys() )
    
    
    def DeleteData( self, name ):
        if name in self.im_data.keys():
            self.DeleteImageData( name )
    
    def Clear( self ):
        self.im_data.clear()
        self.poly_data.clear()
        self.misc_data.clear()
        

def vtkUpdateImage( data, array ):
    vox_data = numpy_support.numpy_to_vtk( array.ravel(), array_type=vtk.VTK_FLOAT )
    shape = [array.shape[2], array.shape[1], array.shape[0]]
    data.SetDimensions( shape )
    data.SetSpacing( [1,1,1] )
    data.SetOrigin( [0,0,0] )
    data.GetPointData().SetScalars( vox_data )


def vtkNumpyToVtkImage( array ):
    im = vtk.vtkImageData()
    vtkUpdateImage( im, array )
    return im
        
        
def vtkFromGraph( graph, data = None ):
    gr_mults = [1,1,1]
    return graph.getVtkPolyData( gr_mults, [0,0,0], gr_poly=data )


def vtkSphereFromParams( pos, rad ):
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter( pos[0], pos[1], pos[2] )
    sphere.SetRadius( rad )
    sphere.Update()
    return sphere
