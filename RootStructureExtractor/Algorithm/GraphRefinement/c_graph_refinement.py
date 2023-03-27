#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import ctypes
import numpy as np

lib_name = "libgraph_refinement.so"


def getLib(path):
    lib_path = path + "/" + lib_name
    if not os.path.isfile(lib_path):
        raise (RuntimeError("Could not locate {0}".format(lib_path)))
    lib = ctypes.cdll.LoadLibrary(lib_path)
    print("Got {0}".format(lib_path))
    return lib


import os
import lib_path

__run_lib_path = lib_path.lib_folder
__run_lib_name = __run_lib_path + "/" + lib_name
try:
    __cost_run_lib = getLib(__run_lib_path)
    # print( "{0} found".format( __run_lib_path +"/" +__run_lib_name ) )
except:
    print("Failed loading {0}. Trying to compile.".format(__run_lib_name))
    try:
        compileLib(os.path.dirname(__file__), True)
        __cost_run_lib = getLib(__run_lib_path)
    except:
        print("Failed to compile {0}. Cannot use c++ perlin noise generation".format(__run_lib_name))
        raise (RuntimeError("Cannot load or compile {0}".format(lib_name)))


def rebuildGraph( graph, rad_map, cost_map, dim_mults, max_cost, num_threads=4 ):
    __cost_run_lib.rebuildGraph( ctypes.c_void_p( graph.getPointer() ),
                                 rad_map.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                 cost_map.ctypes.data_as( ctypes.POINTER( ctypes.c_float ) ),
                                 np.array( rad_map.shape, dtype=np.int32 ).ctypes.data_as( ctypes.POINTER( ctypes.c_int ) ),
                                 np.array( dim_mults, dtype=np.float64).ctypes.data_as( ctypes.POINTER( ctypes.c_double ) ),
                                 ctypes.c_double( max_cost ),
                                 ctypes.c_int( num_threads )
                                )
