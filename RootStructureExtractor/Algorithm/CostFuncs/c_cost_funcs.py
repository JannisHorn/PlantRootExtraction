#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

# import subprocess
import ctypes
import numpy as np

lib_name = "libcost_funcs.so"

# def compileLib( path, output=False ):
#     from subprocess import Popen
#     options = ["g++", "-std=c++17", "-O3", "-Wall" , "-I" +path +"/include", "-I" +path +"/../Utils" , "-fPIC", "-shared", "-o", __run_lib_name]
#     files = [path +"/src/apply_cost_function.cpp"]
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


def applySphereCost( inp_arr, min_occ, min_sphere_occ, max_sphere_r, dim_facs, num_threads = 4 ):
    """
    Given a 3D volume returns the estimated radius by fitting growing spheres at each position

    :param inp_arr: np.array, 3D Volume
    :param min_occ: Float, minimum intensity to count voxel as occupied
    :param min_sphere_occ: Float, minimum percent of sphere occupied to count
    :param max_sphere_r: Int, largest sphere tested
    :param dim_facs: 3-tuple, ratio of voxel edge length
    :param num_threads: Int, max number of threads used
    :return: np.array, Estimated radius per voxel
    """
    out_arr = np.ones( inp_arr.shape, dtype=np.float32 )
    print( inp_arr.max() )
    inp_arr = inp_arr.astype( np.float32 ) /inp_arr.max()
    __cost_run_lib.applySphereCost( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               ctypes.c_int( inp_arr.shape[2] ),
                               ctypes.c_int( inp_arr.shape[1] ),
                               ctypes.c_int( inp_arr.shape[0] ),
                               ctypes.c_double( min_occ ),
                               ctypes.c_double( min_sphere_occ ),
                               ctypes.c_int( max_sphere_r ),
                               dim_facs.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               ctypes.c_int( num_threads )
                              )
    return out_arr



def applyCircleCost( inp_arr, min_occ, min_sphere_occ, max_sphere_r, dim_facs ):
    """
    Given a 2D volume slice, return radius of the largest fitted circle

    :param inp_arr: np.array, 2D Volume slice
    :param min_occ: Float, minimum intensity to count voxel as occupied
    :param min_sphere_occ: Float, minimum percent of sphere occupied to count
    :param max_sphere_r: Int, largest sphere tested
    :param dim_facs: 3-tuple, ratio of voxel edge length
    :return: np.array, Map of largest fitted circle radius per voxel
    """
    out_arr = np.ones( inp_arr.shape, dtype=np.float32 )
    inp_arr = inp_arr.astype( np.float32 ) /inp_arr.max()
    print(inp_arr.shape)
    #print(inp_arr.max())
    __cost_run_lib.applyCircleCost( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               ctypes.c_int( inp_arr.shape[1] ),
                               ctypes.c_int( inp_arr.shape[0] ),
                               ctypes.c_int( 1 ),
                               ctypes.c_double( min_occ ),
                               ctypes.c_double( min_sphere_occ ),
                               ctypes.c_int( max_sphere_r ),
                               dim_facs.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               ctypes.c_int( 1 )
                              )
    return out_arr



def applyRadiusCost( inp_arr, mask_size, num_threads = 4 ):
    """
    Given a 3D radius map, compute the relative radius at each position.
    1.0 if highest radius in mask area.
    0.0 if every sorrounding voxel has even or higher radius.

    :param inp_arr: np.array, 3D radius map
    :param mask_size: Int, amount of voxel per side and dimension to compare to
    :param num_threads: Int, max number of threads used
    :return: np.array, Comparative normalized radius cost
    """
    out_arr = np.zeros( inp_arr.shape, dtype=np.float32 )
    inp_arr = inp_arr.astype( np.float32 ) /inp_arr.max()
    __cost_run_lib.applyRadiusCost( inp_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               out_arr.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                               ctypes.c_int( inp_arr.shape[2] ),
                               ctypes.c_int( inp_arr.shape[1] ),
                               ctypes.c_int( inp_arr.shape[0] ),
                               ctypes.c_int( mask_size ),
                               ctypes.c_int( num_threads )
                              )
    return out_arr

