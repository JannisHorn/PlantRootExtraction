#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import subprocess
import ctypes
import numpy as np

lib_name = "libgraph_pruning.so"

# def compileLib( path, output=False ):
#     from subprocess import Popen
#     options = ["g++", "-std=c++17", "-O3" , "-I" +path +"/include", "-I" +path +"/../Utils" , "-I" +path +"/../Utils/RootExtraction" , "-fPIC", "-shared", "-o", __run_lib_name]
#     files = [path +"/src/graph_pruning.cpp"]
#     compiler = Popen( options+files, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
#     if output:
#         for line in compiler.stdout:
#             print( str(line.decode("utf-8")), end="" )
#         for line in compiler.stderr:
#             print( str(line.decode("utf-8")), end="" )
#     compiler.communicate()
#     comp_out = compiler.returncode
#     if comp_out != 0:
#         raise( RuntimeError( "Failed compiling {0}: {1}".format( lib_name, comp_out ) ) )
        
def getLib( path ):
    lib_path = path +"/" +lib_name
    if not os.path.isfile( lib_path ):
        raise( RuntimeError( "Could not locate {0}".format( lib_path ) ) )
    lib = ctypes.cdll.LoadLibrary(lib_path)
    print( "Got {0}".format( lib_path ) )
    return lib
        
import os
import lib_path
__run_lib_path = lib_path.lib_folder
__run_lib_name = __run_lib_path +"/" +lib_name 
try:
    __cost_run_lib = getLib( __run_lib_path )
    #print( "{0} found".format( __run_lib_path +"/" +__run_lib_name ) )
except:
    print( "Failed loading {0}. Trying to compile.".format( __run_lib_name ) )
    try:
        compileLib( os.path.dirname(__file__), True )
        __cost_run_lib = getLib( __run_lib_path )
    except:
        print( "Failed to compile {0}. Cannot use c++ perlin noise generation".format( __run_lib_name ) )
        raise( RuntimeError( "Cannot load or compile {0}".format( lib_name ) ) )


def skeletonization( radius_map ):
    out_arr = np.zeros( radius_map.shape, dtype=np.float32 )
    print(radius_map.shape)
    __cost_run_lib.skeletonization( radius_map.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                    out_arr.ctypes.data_as(ctypes.POINTER( ctypes.c_float ) ),
                                    ctypes.c_int( radius_map.shape[2] ),
                                    ctypes.c_int( radius_map.shape[1] ),
                                    ctypes.c_int( radius_map.shape[0] )
                                  )
    return out_arr


def grassFire( radius_map ):
    out_arr = np.zeros( radius_map.shape, dtype=np.float32 );
    __cost_run_lib.grassFire( radius_map.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                    out_arr.ctypes.data_as(ctypes.POINTER( ctypes.c_float ) ),
                                    ctypes.c_int( radius_map.shape[2] ),
                                    ctypes.c_int( radius_map.shape[1] ),
                                    ctypes.c_int( radius_map.shape[0] ),
                                  )
    return out_arr


def radiusPruning( radius_arr ):
    #TODO fix seg faults
    out_arr = np.ones( inp_arr.shape, dtype=np.float32 )
    inp_arr = inp_arr.astype( np.float32 ) /inp_arr.max()
    __cost_run_lib.applySphereCost( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               ctypes.c_int( inp_arr.shape[2] ),
                               ctypes.c_int( inp_arr.shape[1] ),
                               ctypes.c_int( inp_arr.shape[0] ),
                               ctypes.c_double( min_occ ),
                               ctypes.c_double( min_sphere_occ ),
                               ctypes.c_int( max_sphere_r ),
                               ctypes.c_int( num_threads )
                              )
    return out_arr


def interpolateGraph( graph, max_diff, path="" ):
    out_graph = ctypes.c_void_p()
    __cost_run_lib.interpolateGraph.restype = ctypes.c_void_p
    c_path = path.encode( "utf-8" )
    out_graph = __cost_run_lib.interpolateGraph( ctypes.c_void_p( graph ), ctypes.c_double( max_diff ), c_path )
    return out_graph


def maskVolumeByGraph( inp_arr, graph, dim_facs, value, rad_rate=1.0 ):
    out_arr = np.copy( inp_arr )
    shape = np.array( inp_arr.shape, dtype=np.int32 )
    __cost_run_lib.maskVolumeByGraph( out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ), 
                                      shape.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                      dim_facs.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                      ctypes.c_void_p( graph ),
                                      ctypes.c_float( value ),
                                      ctypes.c_double( rad_rate ) )
    return out_arr


def pruneShortBranches( graph_ptr, min_len ):
    __cost_run_lib.pruneShortBranches( ctypes.c_void_p( graph_ptr ),
                                       ctypes.c_double( min_len ) )
    
def pruneThinBranches( graph_ptr, min_rad ):
    __cost_run_lib.pruneThinBranches( ctypes.c_void_p( graph_ptr ),
                                       ctypes.c_double( min_rad ) )
#Limited depth search -> 
#Area under curve
