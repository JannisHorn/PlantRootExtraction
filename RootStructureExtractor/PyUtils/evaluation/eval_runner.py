#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""
import numpy as np
import data_wrapper     
import eval_graph
import c_graph_pruning
import time

def extractRootStructure( data, cutoff=None, glength=None, dil=None, n_its=1, exp_mode="linear" ):
    if cutoff is not None: data.extr.cfg.sh_pt_cutoff = cutoff
    if glength is not None: data.extr.cfg.gap_length = glength
    if dil is not None: data.skel.cfg.dil_sum = dil
    st_pt = time.time()
    data.extractVolume( True )
    lcc_pt = time.time()
    #print( "\n\n Sent Its: {} \n\n".format(n_its) )
    data.extractSkeleton( True, n_its, exp_mode )
    ed_pt = time.time()
    time_out = ( lcc_pt-st_pt, ed_pt-lcc_pt, ed_pt-st_pt )
    return data.skel.graph, time_out
    
def getRanges( val, int_type, int_range, int_c ):
    if int_c == 0:
        return []
    vals = []
    int_steps = ( int_range[1] -int_range[0] ) /( int_c-1 )
    #print( "{} => {} +c*{}".format(val, int_range[0], int_steps) )
    for c in range(int_c):
        if int_type == "linear": interval = int_range[0] +c*int_steps
        vals.append( interval )
    return vals
    
def getCutoffRange( data, int_type, int_range, int_c ):
    og_val = data.extr.cfg.sh_pt_cutoff
    rg = [int_range[0] *og_val, int_range[1] *og_val]
    return getRanges( og_val, int_type, rg, int_c )

def getGapLRange( data, int_type, int_range, int_c ):
    og_val = data.extr.cfg.gap_length
    rg = [int_range[0] *og_val, int_range[1] *og_val]
    out = getRanges( og_val, int_type, rg, int_c )
    return [round(el) for el in out]

def getDilSumRange( data, int_type, int_range, int_c ):
    og_val = data.skel.cfg.dil_sum
    rg = [int_range[0] *og_val, int_range[1] *og_val]
    out = getRanges( og_val, int_type, rg, int_c )
    return [round(el) for el in out]
    
def getDilSumRange( data, int_type, int_range, int_c ):
    og_val = data.skel.cfg.dil_sum
    rg = [int_range[0] *og_val, int_range[1] *og_val]
    out = getRanges( og_val, int_type, rg, int_c )
    return [round(el) for el in out]

def getIts():
    return np.arange( 0.5,2.6, 0.5 )


def runExtractionAndEvaluate( dt_pt, ranges ):
    
    def runner( data, ct, gl, ds, ni, em="linear" ):
        data.skel.cfg.lin_int = True
        #data.skel.cfg.z_cut = 0
        graph, times = extractRootStructure( data, ct, gl, ds, ni, em )
        #for it in it_range:
        params = { "ct": ct, "gl":gl, "ds":ds, "ni":ni , "it":-1 }
        #    int_graph = c_graph_pruning.interpolateGraph( graph.graph_wrapper.getPointer(), it )
        dt_pt.evaluate( graph, params, times )
    
    def output( cur, c_runs ):
        print( "============" )
        print( " {0} / {1} ".format( cur, c_runs ) )
        print( "============" )
    
    
    data = data_wrapper.DataWrapper()
    data.load( dt_pt.path )
    cutoff = data.extr.cfg.sh_pt_cutoff 
    glength = data.extr.cfg.gap_length
    dil = data.skel.cfg.dil_sum

    #ct_range = getCutoffRange( data, int_type, int_range, int_c ) 
    #gl_range = getGapLRange( data, int_type, int_range, int_c ) 
    #ds_range = getDilSumRange( data, int_type, int_range, int_c ) 
    #it_range = getIts()
    #print(ct_range)
    #print(gl_range)
    #print(ds_range)
    ct_range = ranges[0]
    gl_range = ranges[1]
    ds_range = ranges[2]
    it_range = ranges[3]
    c_runs = len(ct_range) +len(gl_range) +len(ds_range)
    n_it = 1
    it = 0
    #runner( data, cutoff, glength, dil, 1 )
    #output( it, c_runs )
    #it += 1
    for ct in ct_range:
        runner( data, cutoff *ct, glength, dil, n_it )
        output( it, c_runs )
        it += 1
    for gl in gl_range:
        runner( data, cutoff, int(round(gl *glength)), dil, n_it )
        output( it, c_runs )
        it += 1
    for ds in ds_range:
        runner( data, cutoff, glength, int(round(ds *dil )), n_it )
        output( it, c_runs )
        it += 1
    for its in it_range:
        runner( data, cutoff, glength, dil, its, ranges[4] )
        output( it, c_runs )
        it += 1        
