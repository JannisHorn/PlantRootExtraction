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
for p in os.listdir( os.path.join( path, "build" ) ):
    if "lib" in p:
        lib_path = p 
        break
print( "Found _c_graph_interface folder: {}".format(lib_path) )
sys.path.insert( 0, os.path.join( path, "build/{}".format( lib_path ) ) )
from _c_graph_interface import *
