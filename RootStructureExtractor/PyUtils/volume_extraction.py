#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import numpy as np
import CostFuncs as cf
import ShortestPath as sp
import ExtractGraph as eg

class VolumeExtraction:
    """ Wrapper handling parameter and execution for volume extraction """
    class Config:
        def __init__( self ):
            self.default()
            
        def default( self ):
            self.sphere_occ = 0.75
            self.sphere_rad = 15
            self.cost_w_rad = 1.0
            self.cost_off = 0.00001
            self.sh_pt_idd = 3
            self.sh_pt_cutoff = 150
            self.sh_pt_min_int = 0.5
            self.gap_closing = False
            self.gap_length = 0
            self.fill_graph = False
            
        def __enter__( self ): return self
        
        def __exit__( self, exc_type, exc_val, exc_tb ): pass
            
        def __str__( self ):
            sphere_str = "Sphere Transform: Occ={0}, Rad={1}\n".format( self.sphere_occ, self.sphere_rad )
            cost_str = "Cost: Radius weight={0}, Offset={1}\n".format( self.cost_w_rad, self.cost_off )
            sh_pt_str = "Shortest Path: IdD={0}, Cost Cutoff={1}\n".format( self.sh_pt_idd, self.sh_pt_cutoff )
            if self.gap_closing: gp_str = "Gap Closing: Gap Len={0}".format( self.gap_length )
            else: gp_str = "Gap Closing: False"
            return sphere_str +cost_str +sh_pt_str +gp_str
        
        def fromDic( self, dic ):
            if dic is not None:
                try:
                    errs = []
                    sphere_vals = dic["Sphere"]
                    self.sphere_occ = float(sphere_vals["MinOcc"])
                    self.sphere_rad = int(sphere_vals["MaxRad"])
                    cost_vals = dic["CostFunc"]
                    self.cost_w_rad = float(cost_vals["RadWeight"])
                    self.cost_off = float(cost_vals["Offset"])
                    path_vals = dic["ShortestPath"]
                    self.sh_pt_idd = int(path_vals["Idd"])
                    self.sh_pt_cutoff = float(path_vals["Cutoff"])
                    if path_vals["FillGraph"] == "False":
                        self.fill_graph = False    
                    else: self.fill_graph = True
                    if "GapClosing" in dic:
                        gap_vals = dic["GapClosing"]
                        self.gap_closing = True
                        self.gap_length = int(gap_vals["Length"])
                    self.sh_pt_min_int = float(sphere_vals["MinInt"])
                except KeyError as e:
                    errs.append(str(e))
                    pass
                if any(errs): raise KeyError( ", ".join(errs) )
            else: self.default()
        
        def toItems( self ):
            out = {}
            out["Sphere"] = {"MinOcc": self.sphere_occ, "MaxRad": self.sphere_rad, "MinInt": self.sh_pt_min_int}
            out["CostFunc"] = {"RadWeight": self.cost_w_rad, "Offset": self.cost_off}
            out["ShortestPath"] = {"Idd": self.sh_pt_idd, "Cutoff": self.sh_pt_cutoff, "FillGraph": self.fill_graph}
            if self.gap_closing: out["GapClosing"] = {"Use": self.gap_closing, "Length": self.gap_length}
            return out
        
    def __init__( self ):
        self.cfg = self.Config()
        self.temp_graph = "/temp_graph.xml"
        self.default()
        
    def default( self ):
        self.recom_sphere = True
        self.recom_cost = True
        self.recom_path = True
        self.recom_vol = True        
        self.sphere_cost = None
        self.cost = None
        self.cost_1 = None
        self.cost_2 = None
        self.pred_1 = None
        self.pred_2 = None
        self.gap_map = None
        
    def freeIntermidiateData( self ):
        del self.sphere_cost
        del self.cost
        del self.cost_1
        del self.cost_2
        del self.pred_1
        del self.pred_2
        del self.gap_map
        self.default()
        
        
    def getKeys( self ):
        out = []
        if self.cost is not None: 
            out.append("Cost")
            out.append("Non Gap Cost") 
        if self.cost_1 is not None: 
            out.append("Sphere Cost")
            out.append("Path Cost")
        #if self.gap_map is not None: data_dict["Gap Ident"] = np.where( self.gap_map >= 0, self.gap_map, np.nan )
        if self.gap_map is not None: out.append("Gap Ident")  #np.where( self.gap_map >= 0, 1, 0 )
        return out
        
        
    def getData( self, key ):
        if key == "Cost": return self.cost
        if key == "Non Gap Cost": return np.where( self.cost < (1-self.cfg.gap_per), self.cost, np.nan )
        if key == "Sphere Cost": return self.sphere_cost
        if key == "Path Cost": return np.where( self.cost_1 < 1e+10, self.cost_1, np.nan )
        if key == "Gap Ident": return self.gap_map
        return None
            
            
        
    def costFunction( self, inp_arr, rad_arr, gap_diff ):
        print( "Gap diff for cost func: {0}".format(gap_diff) )
        inp_arr /= inp_arr.max()
        rad_arr /= rad_arr.max()
        i_r_weight = self.cfg.cost_w_rad
        cost_arr = inp_arr +i_r_weight *rad_arr
                
        cost_arr /= cost_arr.max()
        cost_arr -= 1
        cost_arr *= -1
        
        cost_arr += self.cfg.cost_off
        cost_arr /= cost_arr.max()
        
        gap_diff = 1- gap_diff
        if( gap_diff > 0.0 ):
            cost_arr = np.where( cost_arr < gap_diff, cost_arr, cost_arr *10 )
            #cost_arr /= cost_arr.max()
            print( "Cost arr: {0} < {1}".format( cost_arr.min(), cost_arr.max() ) )
        
        #TODO REMOVE TEST
        #cost_off = np.where( cost_arr > 0.9, 5,1 )
        #cost_arr *= cost_off
        return cost_arr
    
    
    def __call__( self, inp_arr, st_pt, dim_mults, clear_mem=True ):
        print( "Starting Volume Extraction:\n===========================" )
        print( self.cfg )
        if clear_mem:
            print( "Removing intermediate Data to save memory" )
            self.freeIntermidiateData()
            self.recom_sphere = True
        if( self.recom_sphere ):
            #print(self.sphere_cost.shape)
            self.sphere_cost = cf.applySphereCost( inp_arr, self.cfg.sh_pt_min_int, self.cfg.sphere_occ, self.cfg.sphere_rad, dim_mults, 2 )
            print( "Got spheres" )
            self.recom_sphere = False
            self.recom_cost = True
        if( self.recom_cost ):
            if not self.cfg.gap_closing:
                self.cfg.gap_per = 0.0
                print(self.cfg.gap_per)
            self.cost = self.costFunction( inp_arr, self.sphere_cost, self.cfg.gap_per )
            self.recom_cost = False
            self.recom_path = True
        if( self.recom_vol ):
            if not self.cfg.gap_closing:
                self.cost_1, self.cost_2, self.pred_1, self.pred_2 = sp.shortestPath( self.cost, st_pt, self.cfg.sh_pt_idd,
                                                                                      self.cfg.sh_pt_cutoff, dim_mults )
            else:
                off_per = self.cfg.cost_off /self.cost.max()
                act_per = 1-( off_per +self.cfg.sh_pt_min_int *(1-off_per) )
                self.cost_1, self.cost_2, self.pred_1, self.pred_2, self.gap_map = sp.shortestPathGapClosing( self.cost, st_pt, self.cfg.sh_pt_idd, self.cfg.sh_pt_cutoff,
                                                                                                              dim_mults, act_per, self.cfg.gap_length )
                
                #path = "/home/jhorn/Documents/Work/DataGeneration/plant-root-MRI-display/root_extraction/"
                #np.save( path +"gap_map.npy", self.gap_map )
                
            self.recom_path = False
            self.recom_vol = True
        if( self.recom_vol ):
            if( not self.cfg.fill_graph ):
                cost_mask = np.where( self.cost_1 <= self.cfg.sh_pt_cutoff, 1, 0 )
                self.volume = cost_mask *np.where( inp_arr > self.cfg.sh_pt_min_int, 1, 0 )
            else:
                where_arr = np.where( inp_arr > self.cfg.sh_pt_min_int, 1.0, 0 )
                where_arr = where_arr.astype( np.float32 )
                _, self.volume = eg.extractGraph( where_arr, self.cost_1, self.cost_2, self.pred_1, self.pred_2,
                                                  st_pt, self.cfg.sh_pt_min_int, self.cfg.sh_pt_cutoff +self.cfg.gap_length*1000, False, self.temp_graph )
                #np.save( path +"neg_extr.npy", np.where( self.volume -inp_arr > 0, 1, 0 ) )

        print( self.sphere_cost.shape )
        #self.saveInterim(inp_arr)
        return self.volume
        
    
            
    def saveInterim( self, vol ):
        path = "/home/jhorn/Documents/Work/PlantRootPaper/segmentation_paper/temps"
        print( "Saving {}".format(path) )
        np.savez( "{}/inp".format(path), vol )
        np.savez( "{}/rad".format(path), self.sphere_cost )
        np.savez( "{}/cost".format(path), np.where(self.cost < 1.0, self.cost, 1.0) )
        np.savez( "{}/p_cost".format(path), self.cost_1 )
        np.savez( "{}/extr".format(path), self.volume )
