#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import Algorithm
import PyUtils
import CostFuncs as cf
import ShortestPath as sp
import ExtractGraph as eg
import GraphPruning as gp
import numpy as np
import time
import PyUtils.root_graph as rg
import skeletonization as skel

def testArr( shape ):
    arr = np.zeros( shape, dtype=np.float32 )
    for x in range( shape[0] ):
        for y in range( shape[1] ):
            for z in range( shape[2] ):
                arr[x,y,z] = x+y+z
    return arr

def costFunction( inp_arr, rad_arr, weight, offset ):
    inp_arr /= inp_arr.max()
    rad_arr /= rad_arr.max()
    i_r_weight = weight
    cost_arr = inp_arr +i_r_weight *rad_arr
    
    cost_arr /= cost_arr.max()
    cost_arr -= 1
    cost_arr *= -1
    
    cost_arr += offset
    return cost_arr


if __name__ == "__main__":
    data_path = "/home/jhorn/Documents/Work/DataGeneration/data/"
    folder_name = "lupine_small/"
    st_pos = np.array([114,137,128], dtype=np.int32)
    #folder_name ="Soil_dap14/"
    #st_pos = np.array([7,125,113], dtype=np.int32)
    file_name = "256x256x128_occupancy.npz"
    #file_name = "512x512x420_occupancy.npz"
    
    data_path = "../"
    folder_name = "TestRoots/"
    st_pos = np.array([300,235,189], dtype=np.int32) #TODO: Find point with highest radius in area!
    file_name = "lupineSmall_real_step719.npz"
    #st_pos = np.array([270,292,47], dtype=np.int32)
    #file_name = "lupine22august_real_step719.npz"
    
    root = np.load( data_path +folder_name +file_name )["arr_0"]
    root = root.astype( np.float32 )
    #root = root[:,:,64:128]
    #st_pos = np.array([114,137,64], dtype=np.int32)
    root /= root.max()
    #root = np.zeros( [20,20,20] )
    #for it in range(20):
    #    root[it,:,:] = it
    dim_mults = np.array([5,1,1], dtype=np.float32)
    st_pt = time.time()
    out = root
    #cost = cf.applySphereCost( out, 0.5, 0.75, 9, dim_mults, 2 )
    print( "Needed {0}s".format( time.time() -st_pt ) )
    print( out.max() )
    #out = costFunction( root, cost, 0.2, 5*10**(-10) )
    print( "{0}<{1}".format( out.min(), out.max() ) )
    
    cost_cutoff = 8 #lupine_small=8
    idd = 3
    st_pt = time.time();
    #cost_1, cost_2, pred_1, pred_2 = sp.shortestPath( out, st_pos, idd, cost_cutoff, dim_mults )
    #cost_1 = cost_1 /cost_1.max()
    print( "Djikstra took {0}s".format(time.time()-st_pt) )
    
    st_pt = time.time()
    min_int = 0.5
    #graph_ptr, ext_arr = eg.extractGraph( root, cost_1, cost_2, pred_1, pred_2, st_pos, min_int, cost_cutoff )
    #print( ext_arr.shape )
    print( "Graph Extraction took {0}s".format(time.time()-st_pt) )
    print( np.where( root >= 0.5, 1.0,0.0 ).sum() )
    graph = rg.RootGraph( "temp.xml" )
    #print( graph )
    mults = [1/root.shape[2],1/root.shape[1],1/root.shape[0]]
    #graph_st = [st_pos[2]/mults[2],st_pos[1]/mults[1],st_pos[1]/mults[1]]
    graph_st =  (st_pos)/root.shape[2] -0.5
    #graph.toVtk( "graph.vtp", mults, graph_st)
    
    ext_arr = np.load( data_path +"extracted.npy" )
    #sci_skel = gp.scipySkeleton( ext_arr )
    #np.save( data_path +"scipy_skel.npy", sci_skel )
    #ext_rad = cf.applySphereCost( ext_arr, 0.5, 1.0, 150, dim_mults, 2 )
    #ext_rad /= ext_rad.max()
    #np.save( data_path +"extracted_rad.npy", ext_rad )
    
    cost_cutoff = 200
    dim_mults[0] = 5
    #ext_cost = costFunction( ext_arr, ext_rad, 1.0, 10**-10 )
    #ext_cost = np.where( ext_arr > 0, ext_cost, ext_cost +2.0 )
    #cost_1, cost_2, pred_1, pred_2 = sp.shortestPath( ext_cost, st_pos, idd, cost_cutoff, dim_mults )
    #graph_ptr, ext_arr = eg.extractGraph( ext_rad, cost_1, cost_2, pred_1, pred_2, st_pos, 0.1, cost_cutoff )
    #skeleton = gp.skeletonization( ext_rad )
    #print( skeleton.max() )
    #graph = rg.RootGraph( "temp.xml" )
    #graph.toVtk( "graph_0.vtp", mults, graph_st)
    print( ext_arr.max() )
    print( ext_arr.shape )
    skeleter = skel.Skeletonization.fromArray( ext_arr, dim_mults )
    graph_ptr = skeleter.paramCall( idd, 2, st_pos )
    graph = rg.RootGraph( "temp.xml" )
    graph.toVtk( "graph.vtp", mults, graph_st )
    
    graph = gp.interpolateGraph( graph_ptr, 2.25 )
    graph = rg.RootGraph( "interpolate.xml" )
    graph.toVtk( "int_graph.vtp", mults, graph_st )
    
    np.save( data_path +"skeleton.npy", skeleton )
    
    np.save( data_path +"sphere_cost.npy", cost )
    np.save( data_path +"cost.npy", out )
    np.save( data_path +"path_cost.npy", cost_1 )
    np.save( data_path +"pred_1_map.npy", pred_1 )
    np.save( data_path +"pred_2_map.npy", pred_2 )
    np.save( data_path +"extracted_0.npy", ext_arr )
