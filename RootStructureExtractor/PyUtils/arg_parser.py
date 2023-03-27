#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import argparse

class ArgParser:
    def __init__( self ):
        self.psr = argparse.ArgumentParser( description=self.dscrStr() )
        self.psr.add_argument( "-r", "--recompile",
                               help="Recompile c-libraries",
                               action="store_true",
                               default=False )
        self.psr.add_argument( "-ns", "--no-settings",
                               help="Load window with default parameters",
                               action="store_true",
                               default=False )
        self.psr.add_argument( "-nd", "--no-data",
                               help="Do not load data from settings",
                               action="store_true",
                               default=False )
        
    def dscrStr( self ):
        return "Program to extract the structure graph fom given root voxel image"
    
    def parse( self ):
        return self.psr.parse_args()
    
