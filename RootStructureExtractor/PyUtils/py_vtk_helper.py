#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from vtk import *
import numpy as np
   
def numpyToVtkImage( array ):
    #a = array.squeeze()
    im = vtkImageData()
    im.SetExtent( 0, a.shape[0]-1, 0, a.shape[1]-1, 0, a.shape[2]-1 )
    #im.SetNumberOfScalarComponents( 1 )
    print( a.size )
    im.AllocateScalars( 10, 1 )
    
    for x in range( a.shape[0] ):
        for y in range( a.shape[1] ):
            for z in range( a.shape[2] ):
                im.SetScalarComponentFromFloat( x,y,z,0,a[x,y,z] )
                
    return im

if __name__ == "__main__":
    a = np.random.rand( 200,200,200 )
    a = a.astype( np.float32 )
    vk = numpyToVtkImage(a)
    print( vk.GetNumberOfPoints() )
    print( "{0} vs {1}".format( a[5,5,5], vk.GetScalarComponentAsFloat(5,5,5,0) ) )
