#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""
import numpy as np

class Data:
    """ Container for all input and generated data """
    def __init__( self, inp_triple=(None, None, None) ):
        self.input = inp_triple[0]
        self.extracted = inp_triple[1]
        self.skeleton = inp_triple[2]
        self.modified = [False, False]
        
    def __del__( self ):
        del( self.input )
        del( self.extracted )
        del( self.skeleton )
        
    def getKeys( self ):
        out = []
        if self.input is not None: out.append("Input")
        if self.extracted is not None: 
            out.append("Extraction")
            out.append("Not Extracted")
            out.append("Extraction/Non Extraction")
        if self.skeleton is not None: out.append("Graph")
        return out
        
    def getData( self, key ):
        if key == "Input": return self.input
        if key == "Extraction": return self.extracted
        if key == "Not Extracted": return self.getNotExtracted()
        if key == "Extraction/Non Extraction": return self.getCombinedExtraction()
        if key == "Graph": return self.skeleton
        return None
    
    def getNotExtracted( self ):
        out = np.where( self.input > 0.0, 1, 0 ).astype( np.float32 )
        out -= self.extracted
        return np.where( out > 0.0, 1, 0 )
    
    def getCombinedExtraction( self ):
        out = np.where( self.input *self.extracted > 0.0, 2, 0 )
        out += self.getNotExtracted()
        return out
