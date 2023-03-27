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

lib_name = "libextract_graph.so"

# def compileLib( path, output=False ):
#     from subprocess import Popen
#     options = ["g++", "-std=c++17", "-O3", "-Wall" , "-I" +path +"/include", "-I" +path +"/../Utils" , "-I" +path +"/../Utils/RootExtraction" , "-fPIC", "-shared", "-o", __run_lib_name]
#     files = [path +"/src/extract_graph.cpp"]
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
    except:
        print( "Failed to compile {0}.".format( __run_lib_name ) )
        raise( RuntimeError( "Cannot load or compile {0}".format( lib_name ) ) )
    

def extractGraph( inp_arr, cost_map_1, cost_map_2, pred_map_1, pred_map_2, start_pt, int_threshold, cost_cutoff, save_grp, path="" ):
    """
    Given a 3D input array, path cost maps and predecessor maps return a graph.
    Given minimum intensity to be included and maximum path cost a per voxel graph.

    :param inp_arr: np.array, 3D intensity map
    :param cost_map_1: np.array, 3D primary cost map
    :param cost_map_2: np.array, 3D secondary cost map
    :param pred_map_1: np.array, 3D primary predecessor map
    :param pred_map_2: np.array, 3D secondary predecessor map
    :param start_pt: 3-tuple, 3D start position
    :param int_threshold: Float, minimum intensity to count as set voxel
    :param cost_cutoff: Float, maximum path cost to include in graph
    :param save_grp: UNUSED
    :param path: UNUSED
    :return: c-pointer to graph object, np.array, array with all voxel in graph are set.
    """
    graph_ptr = ctypes.c_void_p()
    out_arr = np.zeros_like( inp_arr, dtype=np.float32 )
    c_path = path.encode( "utf-8" )
    graph_ptr = __sp_run_lib.extractGraph( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       pred_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       pred_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       ctypes.c_int( inp_arr.shape[2] ),
                                       ctypes.c_int( inp_arr.shape[1] ),
                                       ctypes.c_int( inp_arr.shape[0] ),
                                       start_pt.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       ctypes.c_double( int_threshold ),
                                       ctypes.c_double( cost_cutoff ),
                                       ctypes.c_bool( save_grp ),
                                       ctypes.c_char_p( c_path )
                                      )
    return graph_ptr, out_arr



def extractSkeleton( cmb_map, radius_map, pred_map_1, start_pt, dim_mult, min_cmb, dil_fac, cut_axis, z_cut, qp_min_dist, path="", old_graph_ptr=ctypes.c_void_p(0), seed_qps = False ):
    """
    Given a quench point map, radius estimates and predecessor map compute a curve skeleton.

    :param cmb_map: np.array, Map of comparative radius for quench point detection
    :param radius_map: np.array, Per position radius estimate
    :param pred_map_1: np.array, Per position predecessor map
    :param start_pt: 3-tuple, starting position
    :param dim_mult: 3-tuple, ratio of voxel edge-length
    :param min_cmb: Int, minimum value to count as quench point
    :param dil_fac: Float, Dilation factor to enlarge radius for volume filling
    :param cut_axis: Int, integer code for cut direction
    :param z_cut: Int, Position of cut axis
    :param qp_min_dist: Float, minimum distance qp->start point to be extracted
    :param path: UNUSED
    :param old_graph_ptr: c-pointer, Pointer to old graph to extend
    :param seed_qps: Bool, use leafs of last graph as qp seeds
    :return: c-pointer, extracted skeleton graph, np.array, array with all voxel in graph are set.
    """
    graph_ptr = ctypes.c_void_p()
    print("{},{}".format(pred_map_1.min(), pred_map_1.max()))
    out_arr = np.zeros( cmb_map.shape, dtype=np.float32 )
    pred_map_2 = np.zeros( pred_map_1.shape, dtype=np.int32 )
    cost_map_2 = np.zeros( pred_map_1.shape, dtype=np.float32 )
    #np.save( "test_preds", pred_map_1 )
    __sp_run_lib.extractSkeleton.restype = ctypes.c_void_p
    c_path = path.encode( "utf-8" )
    if cut_axis == 0: cut_axis = 4
    elif cut_axis == 1: cut_axis = 5
    elif cut_axis == 4: cut_axis = 0
    elif cut_axis == 5: cut_axis = 1

    print( old_graph_ptr )
    graph_ptr = __sp_run_lib.extractSkeleton( cmb_map.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       radius_map.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       cost_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       pred_map_1.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       pred_map_2.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       ctypes.c_int( cmb_map.shape[2] ),
                                       ctypes.c_int( cmb_map.shape[1] ),
                                       ctypes.c_int( cmb_map.shape[0] ),
                                       start_pt.ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                       dim_mult.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                       ctypes.c_double( min_cmb ),
                                       ctypes.c_int( dil_fac ),
                                       ctypes.c_int( cut_axis ),
                                       ctypes.c_int( z_cut ),
                                       ctypes.c_double( qp_min_dist ),
                                       ctypes.c_char_p( c_path ),
                                       ctypes.cast( old_graph_ptr, ctypes.c_void_p ),
                                       ctypes.c_bool( seed_qps )
                                      )
    #np.save( "pointers", out_arr )
    return graph_ptr, out_arr

    
    
