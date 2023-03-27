#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import CostFuncs as cf
import ShortestPath as sp
import ExtractGraph as eg
import GraphPruning as gp
import root_graph as rg
import GraphRefinement as gref
import numpy as np
import ctypes
from scipy.ndimage.morphology import binary_closing

class Skeletonization:
    """ Wrapper handling parameter and execution for skeletonization """
    class Config:
        def __init__( self ):
            self.default()
            
        def default( self ):
            self.idd = 3
            self.dil_sum = 200
            self.cut_axis = 0
            self.mask_size = 2
            self.z_cut = 0
            self.lin_int = False
            self.lin_int_diff = 2.25
            self.qp_min_dist = 0.0
            self.min_br_length = 0.0
            self.use_old_graph = False
            self.min_br_radius = 0.0
            self.thin_roots = True

        def __enter__( self ): return self
        
        def __exit__( self, exc_type, exc_val, exc_tb ): pass
    
        def __str__( self ):
            skel_str = "Skeletonization: Idd={0}, DilSum={1}, CutAxis={2}, ZCut={3}, MaskSize={4}\n".format( self.idd, self.dil_sum, self.cut_axis, self.z_cut, self.mask_size )
            int_str = "Interpolation: Use={0}, MaxDiff={1}\n".format( self.lin_int, self.lin_int_diff )
            return skel_str +int_str
        
        def fromDic( self, dic ):
            if dic is not None:
                try:
                    errs = []
                    self.idd = int(dic["Idd"])
                    self.dil_sum = int(dic["Dilation"])
                    if dic["LinInter"] == "False":
                        self.lin_int = False
                    else: self.lin_int = True
                    self.lin_int_diff = float(dic["LinInterDiff"])
                    self.z_cut = int(dic["ZCut"])
                    self.cut_axis = int(dic["CutAxis"])
                    self.mask_size = int(dic["MaskSize"])
                    self.qp_min_dist = float(dic["QpMinDist"])
                    self.min_br_length = float(dic["MinBrLength"])
                    self.min_br_radius = float(dic["MinBrRadius"])
                except KeyError as e:
                    errs.append(str(e))
                    pass
                if any(errs): raise KeyError( ", ".join(errs) )
            else: self.default()
        
        def toItems( self ):
            out = {}
            out["Idd"] = self.idd
            out["Dilation"] = self.dil_sum
            out["MaskSize"] = self.mask_size
            out["ZCut"] = self.z_cut
            out["CutAxis"] = self.cut_axis
            out["QpMinDist"] = self.qp_min_dist
            out["LinInter"] = self.lin_int
            out["LinInterDiff"] = self.lin_int_diff
            out["MinBrLength"] = self.min_br_length
            out["MinBrRadius"] = self.min_br_radius
            return out
    
    def __init__( self ):
        self.cost_cutoff = 100000
        self.temp_graph = "/temp_graph.xml"
        self.cfg = self.Config()
        self.recom_skel = True
        self.recom_int = True
        self.radius = None
        self.ext_rad_pr = None
        self.cost = None
        self.cost_1 = None
        self.old_graph = None
        self.cmb_arr = None
    
    def freeIntermidiateData( self ):
        del self.ext_rad_pr
        del self.ext_rad_norm
        del self.ext_rad_norm
        del self.cost
        del self.cost_1
        del self.cost_2
        del self.pred_1
        del self.pred_2
        self.default()
    
    
    def getKeys( self ):
        out = []
        if self.ext_rad_pr is not None: out.append("Extraction Rad")
        if self.cost is not None: out.append("Skel Cost")
        if self.cost_1 is not None: out.append("Skel Path Cost")
        if self.old_graph is not None: out.append( "Old Graph" )
        if self.radius is not None: out.append( "Radius Map" )
        if self.cmb_arr is not None: out.append( "CMB" )
        return out
    
    def getData( self, key ):
        if key == "Extraction Rad": return np.where( self.ext_rad_pr > 0, self.ext_rad_pr, np.nan ) 
        if key == "Skel Cost": return np.where( self.cost < 100, self.cost, np.nan )
        if key == "Skel Path Cost": return self.cost_1
        if key == "Old Graph": return self.old_graph
        if key == "Radius Map": return self.radius
        if key == "CMB": return self.cmb_arr
        return None
    
    @classmethod
    def fromArray( skel, inp_arr, dim_mults ):
        skel = Skeletonization()
        skel.inp = inp_arr
        skel.cost_cutoff = 100000
        skel.dim_mults = dim_mults
        return skel
    
    def getRadius( self, inp, occ ):
        radius = cf.applySphereCost( inp, 0.5, occ, 50, self.dim_mults, 2 )
        ext_rad = cf.applyRadiusCost( radius, self.cfg.mask_size, 2 )
        ext_rad_pr = ext_rad +np.where( inp > 0.5, 5.0, 0.0 )
        ext_rad_norm = ext_rad_pr /ext_rad_pr.max()
        return radius, ext_rad_norm
    
    def costFunction( self, rad_cost ):
        offsets = np.where( rad_cost > 0.0, 0.0, self.cost_cutoff )
        cost = rad_cost *-1
        #self.cost -= np.where( self.inp > 0.5, 0.01, 0.0 )
        #self.cost /= self.cost.max()
        cost += 1
        cost += offsets
        cost = cost.astype( np.float32 )
        return cost
    
    def paramCall( self, idd, dil_sum, st_pos ):
        self.cfg.idd = idd
        self.cfg.dil_sum = dil_sum
        self.cfg.temp_file = ""
        self.cfg.temp_graph = "temp.xml"
        return self.__call__( self.inp, st_pos, self.dim_mults )
    
    def __call__( self, inp, st_pos, dim_mults, its=1, mode="linear" ):
        #print( "\n\n GOT ITS: {}\n\n".format( its ) )
        if its > 1:
            return self.iterativeExpansion( inp, st_pos, dim_mults, its, mode )
        #TODO infinite loop
        print( self.cfg )
        self.inp = inp
        #self.inp = binary_closing( self.inp, iterations = 6 )
        self.dim_mults = dim_mults
        print( "Got Cost Function" )
        self.radius = cf.applySphereCost(inp, 0.5, 0.75, 50, self.dim_mults, 2)
        _, self.rad_cost = self.getRadius(self.inp, 0.99 )
        print( "Got Cmb" )
        self.cost = self.costFunction( self.rad_cost )
        self.cmb_arr = gp.skeletonization( self.cost *-1 )#self.radius)
        if self.cfg.use_old_graph:
            if self.old_graph is None:
                raise RuntimeError( "No old graph loaded!" )
            mask = gp.maskVolumeByGraph(np.zeros_like(self.cost), self.old_graph.getPointer(), dim_mults, 1.0, 1.0)
            mask = np.where(inp > 0.0, mask, 0.0)
            self.cost = np.where( mask > 0.0, 0.0, self.cost )
            graph_ptr = self.old_graph.getPointer()
        else:
            graph_ptr = 0
        print( "Got full Cost" )
        self.cost_1, cost_2, pred_1, pred_2 = sp.shortestPathDirPenalty( self.cost, self.radius, st_pos, self.cfg.idd, self.cost_cutoff, self.dim_mults, 2.0 )
        print("Got Paths")
        #self.ext_rad = cf.applySphereCost( self.inp, 0.5, 0.75, 50, self.dim_mults, 2 )
        graph_ptr,_ = eg.extractSkeleton( self.cmb_arr, self.radius, pred_1, st_pos, self.dim_mults, 20, self.cfg.dil_sum,
                                          self.cfg.cut_axis, self.cfg.z_cut, self.cfg.qp_min_dist, self.temp_graph, graph_ptr )

        #graph_ptr,_ = eg.extractSkeleton( cmb_arr, self.radius, pred_1, st_pos, self.dim_mults, 20, self.cfg.dil_sum,
        #                                  self.cfg.cut_axis, self.cfg.z_cut, self.cfg.qp_min_dist, self.temp_graph, graph_ptr, True )

        print( "Python got: {0}".format( graph_ptr ) )
       
        #masked_cost = gp.maskVolumeByGraph( np.zeros_like( self.cost ), graph_ptr, dim_mults, 1.0, 1.0 )
        #np.savez( "mask_test", masked_cost )

        #if self.cfg.thin_roots:
        #    mask = gp.maskVolumeByGraph(np.zeros_like(self.cost), graph_ptr, dim_mults, 1.0, 1.0)
        #    mask = np.where(inp > 0.0, mask, 0.0)
        #    self.cost = np.where( mask > 0.0, 0.0, self.cost )
        #    graph_ptr, _ = eg.extractSkeleton(self.cmb_arr, self.radius, pred_1, st_pos, self.dim_mults, 1, self.cfg.dil_sum,
        #                                      self.cfg.cut_axis, self.cfg.z_cut, self.cfg.qp_min_dist, self.temp_graph, graph_ptr)

        self.graph = rg.RootGraph.fromCGraph( graph_ptr )
        print( "Repair Predecessors, Radius and TipRadius." )
        self.graph.repairPreds()
        self.graph.repairRadius()
        self.graph.repairTips()
        gp.pruneShortBranches( self.graph.getPointer(), self.cfg.min_br_length )
        gp.pruneThinBranches( self.graph.getPointer(), self.cfg.min_br_radius )
        self.graph.evaluateRootID()
        if self.cfg.lin_int:
            int_graph = gp.interpolateGraph( self.graph.getPointer(), self.cfg.lin_int_diff, self.temp_graph )
            print( "Got interpolated graph" )
            #print(self.graph.getDensePointList(1.0))
            self.graph = rg.RootGraph.fromCGraph( int_graph )
            #gref.rebuildGraph(self.graph, self.radius, self.rad_cost, self.dim_mults, 50.0, 1)
        return self.graph


    def iterativeExpansion( self, inp, st_pos, dim_mults, deep_its, mode="linear" ):

        def subdivideInput( mode ):
            shape = np.zeros( [deep_its+1, 3], dtype=np.int32 )
            need_steps = np.array( inp.shape, dtype=np.int32 )
            shape[deep_its,:] = need_steps
            for it in range(3):
                need_steps[it] = max( st_pos[it], inp.shape[it]-st_pos[it] )
            temp_shape = np.zeros( [3] )
            for d_it in range( deep_its-1 ):
                for it in range(3):
                    if mode == "linear":
                      temp_shape[it] = need_steps[it]/deep_its
                    elif mode == "log":
                      numerator = 2**(deep_its-d_it-1)
                      temp_shape[it] = need_steps[it]/numerator
                      print( "Numerator: {}".format(numerator) )
                    else: raise RuntimeError( "subdivideInput: Unknown mode: {}".format(mode) )
                shape[d_it+1,:] = shape[d_it,:] +temp_shape
            print( "Iteration steps: {}".format( shape ) )
            return shape
            
        def maskCost( size, cost ):
            upper = [int(min(st_pos[0]+size[0], inp.shape[0])),
                     int(min(st_pos[1]+size[1], inp.shape[1])),
                     int(min(st_pos[2]+size[2], inp.shape[2]))]
            lower = [int(max(st_pos[0]-size[0], 0)),
                     int(max(st_pos[1]-size[1], 0)),
                     int(max(st_pos[2]-size[2], 0))]
            print( "L: {}, U: {}".format( lower, upper ) )
            cur_cost = np.full_like( inp, np.inf )
            cur_cost[lower[0]:upper[0], lower[1]:upper[1], lower[2]:upper[2]] = cost[lower[0]:upper[0], lower[1]:upper[1], lower[2]:upper[2]]
            return cur_cost
        
        print( self.cfg )
        print( "Iterative Expansion: {}".format( deep_its ) )
        self.inp = inp
        self.dim_mults = dim_mults
        self.radCost()
        shape = subdivideInput(mode)
        print( "Got Cost Function" )
        cmb_arr = gp.skeletonization( self.ext_rad_norm )
        self.costFunction()
        masked_cost = maskCost( shape[0,:], self.cost )
        np.savez( "masked_cost", masked_cost )
        graph_ptr = ctypes.c_void_p()
        for it in range( deep_its ):
            print( "Run iteration {}: Shape: {}".format( it, deep_its*(it+1) ) )
            masked_cost = maskCost( shape[it,:], masked_cost )
            self.cost_1, cost_2, pred_1, pred_2 = sp.shortestPathDirPenalty( masked_cost, st_pos, self.cfg.idd, self.cost_cutoff, self.dim_mults, 1.0 )
            #self.ext_rad = cf.applySphereCost( self.inp, 0.5, 0.75, 50, self.dim_mults, 2 )
            cmb_masked = np.where( self.cost_1 > self.cost_cutoff, 0, cmb_arr )
            graph_ptr,_ = eg.extractSkeleton( cmb_masked, self.ext_rad_pr, pred_1, st_pos, self.dim_mults, 20, self.cfg.dil_sum,
                                              self.cfg.cut_axis, self.cfg.z_cut, self.cfg.qp_min_dist, self.temp_graph, graph_ptr )
            print( "Python got: {0}".format( graph_ptr ) )
            mask = gp.maskVolumeByGraph( np.zeros_like( self.cost ), graph_ptr, dim_mults, 1.0, 1.0 )
            mask = np.where( inp > 0.0, mask, 0.0 )
            masked_cost = np.where( mask > 0.0, 0.0, self.cost )
            np.savez( "mask_test_{}".format(it), masked_cost/masked_cost.max() )
        
        np.savez( "mask_test", masked_cost )
        
        print("Finished")
        if self.cfg.lin_int:
            graph_ptr = gp.interpolateGraph( graph_ptr, self.cfg.lin_int_diff, self.temp_graph )
        print(graph_ptr)
        self.graph = rg.RootGraph.fromCGraph( graph_ptr )
        print("Got PyGraph")
        #self.graph = rg.RootGraph( self.temp_graph )
        return self.graph
        
    
    
    #1st search main root
    #plan using dynamic for each branch
    #apply short acceleration into each direction (28)
    #weight costs by acceleration
    #accumulate cost over all cells
    # Search-based MotionPlanning using linear quadratic minimum time control , Liu
    # simple 2D dynamic system: pos, vel
    # can increase runtime significantly, max need some adjustmenets regarding djikstra->A*
