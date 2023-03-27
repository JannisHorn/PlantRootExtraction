#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.ndimage import zoom

class DatatypeBase:
    """ Base class for non .npy files """
    def __init__( self ):
        self.type = None
        self.data_name = ""
        
    def __call__( self ):
        return self.type
    
    def getType( self ):
        return self.type
    
    def importFile( self, fname ):
        raise RuntimeError( "Import Method for Datatype not reimplemented" )
    
    
class RawData( DatatypeBase ):
    """ Contains all information needed to load .raw files 
        dt should be numpy datatype
    """
    def __init__( self ):
        super().__init__()
        self.type = "raw"
        self.shape = [0,0,0]
        self.dt = None
        self.swap_axes = False
        self.swap_byte_order = False
        
        
    def importFile( self, fname ):
        try:
            data = np.fromfile( fname, dtype=self.dt )
            if self.swap_byte_order:
                data = data.byteswap( )
            data = data.reshape( self.shape ).astype( np.float32 )
            data /= data.max()
            if self.swap_axes:
                data = np.swapaxes( data, 0,2 )
            print( "Got raw data" )
            self.data_name = fname.split( "/" )[-1]
            return data
        except IOError as e:
            raise IOError( "Import Raw Error: {0}".format( e ) )
            
            
        
class TifData( DatatypeBase ):
    """ Holds information and transforms .tif stack to numpy arr 
        To correctly work the 3D slices have to be named "...X.tif" 
        X being slice number having the same number of digits per file!
        File name format only exrtacted once
    """
    def __init__( self ):
        super().__init__()
        self.type = "tif"
        self.shape = [0,0,0]
        self.rescale_fac = 1
        self.valid_exts = ["tif", "tiff"]
        
        
    def getFileNameFormat( self, file_name ):
        file_no_ext = file_name.split( "." )[0]
        num_it = 0
        for c in reversed( file_no_ext ):
            if c.isdigit(): num_it += 1
            else: break
        print(num_it)
        return num_it
            
    
    def idFromName( self, file_name ):
        return int( file_name.split( "." )[0][-self.num_length:] )
    
    
    def getIndexAndSlice( self, file_name ):
        try:
            npslice = plt.imread( os.path.join( self.path, file_name ) )
            ind = self.idFromName( file_name )
            return (ind, npslice.astype( np.float32 ))
        except IOError as e:
            raise e
       
        
    def importSlice( self, fslice ):
        try:
            if fslice.split( "." )[-1] in self.valid_exts:
                ind, sli = self.getIndexAndSlice( fslice )
                self.inds.append( ind )
                self.slics.append( zoom( sli.astype(np.float64), (self.rescale_fac,self.rescale_fac) ) )
        except IOError as e:
            print( "Cannot load {0}".format( fslice ) )
            raise( e )        
        
                
    def importFile( self, fname ):
        try:
            self.path = "/".join( fname.split("/")[:-1] )
            print( "Loading: {}/{}".format( self.path, "".join( (fname.split("/")[-1]).split(".")[:-1]) ) )
            file_list = [ f for f in os.listdir( self.path ) if os.path.isfile( os.path.join(self.path, f) ) ]
            self.num_length = self.getFileNameFormat( file_list[0] )
            
            self.inds = []
            self.slics = []
            for it, file in enumerate( file_list ):
                self.importSlice( file )
                print( "\rSlice {0}/{1}".format( it, len( file_list ) ), end="" )
            offset = min(self.inds)
            
            out = np.zeros( ( len( self.slics ), self.slics[0].shape[0], self.slics[0].shape[1] ), dtype=self.slics[0].dtype )
            for it, ind in enumerate(self.inds):
                out[ind-offset,:,:] = self.slics[it]
            
            print( "\nNumpyArray filled" )
            del self.inds
            del self.slics
            
            out = zoom( out, ( self.rescale_fac, 1, 1 ) )
            out = out.astype( np.float32 )
            out -= out.min()
            out /= out.max()
            print( "New bounds: {0} < {1}".format( out.min(), out.max() ) )
            
            data_name = fname.split("/")[-1]
            data_name = "".join( data_name.split(".")[:-1] )
            data_name = data_name[:-self.num_length]
            if data_name[-1] == "_": data_name = data_name[:-1]
            self.data_name = "{}_{:3.2f}".format( data_name, self.rescale_fac )
            print( "Data Name: {}".format(self.data_name) )
            return out
        except (IOError, IndexError) as e:
            raise IOError( str(e) )
