#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import ctypes
__libc = ctypes.CDLL( None )

class Logger():
    def __init__( self, path ):
        self.path = path
        
    def redirectStdOut( self ):
        
