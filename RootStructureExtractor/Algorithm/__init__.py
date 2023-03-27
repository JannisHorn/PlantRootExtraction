#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import sys
import os
path = os.path.dirname(__file__)
sys.path.insert( 0, path )

if not os.path.isdir( path +"/Libs" ):
  os.mkdir( path +"/Libs" )
  
def forceRecompile():
    libs = ["lib_cost_funcs.so", "lib_extract_graph.so", "lib_graph_pruning.so", "lib_shortest_path.so"]
    for lib in libs:
        fname = os.path.join( path +"/Libs", lib )
        try:
            if os.path.isfile( fname ):
                os.remove( fname )
        except Exception as e:
            print( e )
