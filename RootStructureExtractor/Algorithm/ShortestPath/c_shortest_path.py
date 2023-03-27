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

lib_name = "libshortest_path.so"

# def compileLib( path, output=False ):
#     from subprocess import Popen
#     options = ["g++", "-std=c++17", "-O3", "-Wall" , "-I" +path +"/include", "-I" +path +"/../Utils", "-I" +path +"/../Utils/RootExtraction" , "-fPIC", "-shared", "-o", __run_lib_name]
#     files = [path +"/src/adapted_djikstra.cpp"]
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
    __sp_run_lib = getLib( __run_lib_path )
    #print( "{0} found".format( __run_lib_path +"/" +__run_lib_name ) )
except:
    print( "Failed loading {0}. Trying to compile.".format( __run_lib_name ) )
    try:
        compileLib( os.path.dirname(__file__), True )
        __sp_run_lib = getLib( __run_lib_path )
    except RuntimeError as e:
        print( "Failed to compile {0}: {1}.".format( __run_lib_name, e ) )
        raise( RuntimeError( "Cannot load or compile {0}".format( lib_name ) ) )
    

def shortestPath( inp_arr, start_pt, idd, cost_cutoff, dim_mults ):
    """
    Given a 3D cost map, return the per voxel shortest path and second shortest path.
    Uses Dijkstra shortest path.

    :param inp_arr: np.array, 3D cost map
    :param start_pt: 3-tuple, starting position
    :param idd: Int, Neighborhood definition for node expansion
    :param cost_cutoff: Maximum path cost to evaluate
    :param dim_mults: 3-tuple, ratio of voxel edge-length
    :return: Cost/Predecessor map for 1st and 2nd shortest path
    """
    cost_map_1 = np.zeros_like( inp_arr, dtype=np.float32 )
    pred_map_1 = np.zeros_like( inp_arr, dtype=np.int32 )
    cost_map_2 = np.zeros_like( inp_arr, dtype=np.float32 )
    pred_map_2 = np.zeros_like( inp_arr, dtype=np.int32 )
    #dim_mults = np.flip( dim_mults, 0 ).astype( np.float32 )
    __sp_run_lib.djikstraShortestPath( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       pred_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       pred_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       ctypes.c_int( inp_arr.shape[2] ),
                                       ctypes.c_int( inp_arr.shape[1] ),
                                       ctypes.c_int( inp_arr.shape[0] ),
                                       start_pt.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       ctypes.c_int( idd ),
                                       ctypes.c_float( cost_cutoff ),
                                       dim_mults.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) )
                                      )
    return cost_map_1, cost_map_2, pred_map_1, pred_map_2


def shortestPathDirPenalty( inp_arr, rad_arr, start_pt, idd, cost_cutoff, dim_mults, dir_pen ):
    """
    Given a 3D cost map, return the per voxel shortest path and second shortest path.
    Uses Dijkstra shortest path with direction penalty based on predecessor direction.

    :param inp_arr: np.array, 3D cost map
    :param start_pt: 3-tuple, starting position
    :param idd: Int, Neighborhood definition for node expansion
    :param cost_cutoff: Maximum path cost to evaluate
    :param dim_mults: 3-tuple, ratio of voxel edge-length
    :param dir_pen: Cost multiplier for incongruent direction
    :return: Cost/Predecessor map for 1st and 2nd shortest path
    """
    cost_map_1 = np.zeros_like( inp_arr, dtype=np.float32 )
    pred_map_1 = np.zeros_like( inp_arr, dtype=np.int32 )
    cost_map_2 = np.zeros_like( inp_arr, dtype=np.float32 )
    pred_map_2 = np.zeros_like( inp_arr, dtype=np.int32 )
    #dim_mults = np.flip( dim_mults, 0 ).astype( np.float32 )
    __sp_run_lib.djikstraShortestPathDirection( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                                rad_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                                cost_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                                cost_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                                pred_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                                pred_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                                ctypes.c_int( inp_arr.shape[2] ),
                                                ctypes.c_int( inp_arr.shape[1] ),
                                                ctypes.c_int( inp_arr.shape[0] ),
                                                start_pt.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                                ctypes.c_int( idd ),
                                                ctypes.c_float( cost_cutoff ),
                                                dim_mults.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                                ctypes.c_float( dir_pen )
                                               )
    return cost_map_1, cost_map_2, pred_map_1, pred_map_2


def shortestPathGapClosing( inp_arr, start_pt, idd, cost_cutoff, dim_mults, gap_per, gap_length ):
    """
    Given a 3D cost map, return the per voxel shortest path and second shortest path.
    Uses Dijkstra shortest path with gap closing modification.

    :param inp_arr: np.array, 3D cost map
    :param start_pt: 3-tuple, starting position
    :param idd: Int, Neighborhood definition for node expansion
    :param cost_cutoff: Maximum path cost to evaluate
    :param dim_mults: 3-tuple, ratio of voxel edge-length
    :param gap_per: Float, minimum cost percentage to be considered gap
    :param gap_length: Int, maximum gap length to bridge
    :return: Cost/Predecessor map for 1st and 2nd shortest path, 3D volume holding all gaps
    """
    cost_map_1 = np.zeros_like( inp_arr, dtype=np.float32 )
    pred_map_1 = np.zeros_like( inp_arr, dtype=np.int32 )
    cost_map_2 = np.zeros_like( inp_arr, dtype=np.float32 )
    pred_map_2 = np.zeros_like( inp_arr, dtype=np.int32 )
    gap_map = np.full_like( inp_arr, -1, dtype=np.int32 )
    #dim_mults = np.flip( dim_mults, 0 ).astype( np.float32 )
    __sp_run_lib.djikstraGapClosing( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       pred_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       pred_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       gap_map.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       ctypes.c_int( inp_arr.shape[2] ),
                                       ctypes.c_int( inp_arr.shape[1] ),
                                       ctypes.c_int( inp_arr.shape[0] ),
                                       start_pt.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       ctypes.c_int( idd ),
                                       ctypes.c_float( cost_cutoff ),
                                       dim_mults.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       ctypes.c_double( gap_per ),
                                       ctypes.c_int( gap_length )
                                      )
    return cost_map_1, cost_map_2, pred_map_1, pred_map_2, gap_map
