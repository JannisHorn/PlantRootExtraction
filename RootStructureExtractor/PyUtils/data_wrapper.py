#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import numpy as np
from CostFuncs import applyCircleCost
import skeletonization as skeletor
import volume_extraction as vol_extr
import file_handler as fh
import data_container as dt_ct

class DataWrapper:
    """ 
    Container storing input file and data fields correspondingly generated
    
    Handles Data and saving loading, Gui access and data availability
    """
    
    class Config:
        """ Container storing dataset parameters """
        def __init__( self ):
            self.default()
            
        def default( self ):
            self.shape = np.array([0,0,0], dtype=np.int32)
            self.st_pt = np.array([0,0,0], dtype=np.int32)
            self.dim_mults = np.array([1,1,1], dtype=np.float32)
            self.ages = [0,1]
            self.max_type = 3
            self.vox_res = 1.0
            self.use_extraction = False
        
        def __str__( self ):
            out = ""
            out += "Shape: {0}\n".format( self.shape )
            out += "StartPos: {0}\n".format( self.st_pt )
            out += "DimMults: {0}\n".format( self.dim_mults )
            out += "Ages: {0}-{1}\n".format( self.ages[0], self.ages[1] )
            out += "MaxType: {0}\n".format( self.max_type )
            out += "Voxel Res: {0}".format( self.vox_res )
            return out
        
        def fromDic( self, dic ):
            def from3DtoNp( pt, dtype ):
                out = np.zeros(3, dtype=dtype)
                out[0] = pt["x"]
                out[1] = pt["y"]
                out[2] = pt["z"]
                return out
            
            if dic is not None:
                try:
                    errs = []
                    self.st_pt = from3DtoNp(dic["StartPos"], np.int32)
                    self.dim_mults = from3DtoNp(dic["DimMults"], np.float32)
                    self.ages = [ int(dic["MinAge"]), int(dic["MaxAge"]) ]
                    self.max_type = int(dic["MaxType"])
                    self.vox_res = float(dic["VoxelRes"])
                except KeyError as e:
                    errs.append(str(e))
                    pass
                if any(errs): raise KeyError( ", ".join(errs) )
            else: self.default()
        
        def toItems( self ):
            out = {}
            out["Shape"] = self.shape
            out["StartPos"] = self.st_pt
            out["DimMults"] = self.dim_mults
            out["MinAge"] = self.ages[0]
            out["MaxAge"] = self.ages[1]
            out["MaxType"] = self.max_type
            out["VoxelRes"] = self.vox_res
            return out
            
    
    class Status:
        """ Container to display relevant information about the data """
        def __init__( self, file, data, cfg, ecfg, scfg ):
            self.name = [file.file_name,""]
            if data is not None:
                self.has_data = [data.input is not None, data.extracted is not None, data.skeleton is not None]
            else:
                self.has_data = [None, None, None]
            self.items = {"Input": cfg.toItems()}
            self.items["Extraction"] = ecfg.toItems()
            self.items["Skeletonization"] = scfg.toItems()
            
    
    def __init__( self ):
        self.data = None
        self.file = None
        self.cfg = self.Config()
        self.extr = vol_extr.VolumeExtraction()
        self.skel = skeletor.Skeletonization()
        
    
    def valid( self ):
        return self.data is not None
    
    
    def validFile( self ):
        return self.file is not None
    
    def validExtraction( self ):
        return self.data.extracted is not None
    
    
    def getKeys( self ):
        data_keys = self.data.getKeys()
        data_keys += self.extr.getKeys()
        data_keys += self.skel.getKeys()
        return data_keys
    
    def getData( self, key ):
        dt = self.data.getData( key )
        if dt is not None: return dt
        dt = self.extr.getData( key )
        if dt is not None: return dt
        dt = self.skel.getData( key )
        if dt is not None: return dt        
        raise KeyError( "Cannot find key: {} for visualization".format(key) )
    
    def getStatus( self ):
        if not self.validFile:
            return None
        else:
            out = self.Status( self.file, self.data, self.cfg, self.extr.cfg, self.skel.cfg )
            return out
        
    def name( self ):
        return str( self.file )
        
    def getPath( self ):
        if self.file is not None:
            return self.file.path
        else:
            return ""
    
    
    def load( self, fname: str ):
        try:
            file = fh.DataFile( fname )
            pre_cfgs, pre_data = file.load()
            try:
                errs = [None, None, None]
                try:
                    self.cfg.fromDic( pre_cfgs[0] )
                except KeyError as e: errs[0] = e
                try:
                    self.extr.cfg.fromDic( pre_cfgs[1] )
                except KeyError as e: errs[1] = e
                try:
                    self.skel.cfg.fromDic( pre_cfgs[2] )
                except KeyError as e: errs[2] = e
                if any(errs): raise KeyError( "{}, {}, {}".format( errs[0], errs[1], errs[2] ) )
            except KeyError as e:
                print( "Error: Config Key wrong: {0}".format(str(e)) )
                #raise IOError( "Invalid Config file: KeyError {0}".format( str(e) ) )
            finally:
                del( self.data )
                self.data = dt_ct.Data( pre_data )
                print( "New File Loader: {0}".format( file ) )
                self.file = file
                self.cfg.shape = self.data.input.shape
                self.extr.recom_sphere = True
        except (IOError, ValueError) as e:
            print( "IOError during loading: {0}".format( e ) )
            raise IOError( e )
    
    def loadFile( self, fname: str ):
        try:
            file = fh.DataFile( fname )
            pre_cfgs, pre_data = file.load()
            try:
                self.cfg.fromDic( pre_cfgs[0] )
                self.extr.cfg.fromDic( pre_cfgs[1] )
                self.skel.cfg.fromDic( pre_cfgs[2] )
                self.data = dt_ct.Data( pre_data )
            except KeyError as e:
                print( "Error: Config Key wrong: {0}".format(str(e)) )
                raise IOError( "Invalid Config file: KeyError {0}".format( str(e) ) )
            finally:
                print( "New File Loader: {0}".format( file ) )
                self.file = file
                self.cfg.shape = self.data.input.shape
        except IOError as e:
            raise e
    
    def loadCfg( self, fname: str ):
        try:
            cfgs = fh.DataFile.loadCfg( fname )
            self.cfg.fromDic( cfgs[0] )
            self.extr.cfg.fromDic( cfgs[1] )
            self.skel.cfg.fromDic( cfgs[2] )
        except KeyError as e:
            print( "Error: Config Key wrong: {0}".format(str(e)) )
            raise IOError( "Invalid Config file: KeyError {0}".format( str(e) ) )
            
    def loadInput( self, fname: str ):
        try:
            self.input = fh.DataFile.loadFile( fname )
            if self.file is None:
                self.file = fh.DataFile( fname )
            else: self.file.setPath( fname )
        except IOError as e:
            raise e
            
    def loadExtr( self, fname: str ):
        try:
            self.extracted = fh.DataFile.loadFile( fname )
        except IOError as e:
            raise e
                          
    def loadSkel( self, fname ): #TODO
        try:
            pass
        except IOError as e:
            raise e
    
    def importInput( self, fname: str, dt_cfg ):
        try:
            file = fh.DataFile( fname )
            data = dt_ct.Data( file.importFile( fname, dt_cfg ) )
            self.cfg.shape = data.input.shape
            self.file = file
            self.data = data
        except IOError as e:
            raise e
        
    def save( self, fname: str="" ):
        try:
            self.file.save( fname, self.data, self.cfg, self.extr.cfg, self.skel.cfg )
            self.data.modified = [False, False]
        except IOError as e:
            raise e

    def saveGraph( self, fname: str ):
        try:
            self.file.saveGraphAsXml( fname, self.data )
        except IOError as e:
            raise e
            
    #TODO add min_int to datacontroller
    #Heuristic find upper bound by upper noise 
    def findStartPoint( self, depth ):
        max_rad = int(np.ceil(max( self.data.input.shape[1], self.data.input.shape[2] ) /10))
        print( "Depth:{}".format(depth) )
        cut = applyCircleCost( self.data.input[depth,:,:], 0.5, 0.75, max_rad, self.cfg.dim_mults )
        #print(cut)
        #cut = c_rad#[depth,:,:]
        #np.savez("/home/jhorn/links/root_extraction/Data/cut.npz", cut)
        #np.savez("/home/jhorn/links/root_extraction/Data/real.npz", self.data.input[depth,:,:])
        st_pt = np.unravel_index( np.argmax(cut), cut.shape )
        return st_pt[0], st_pt[1]
    
    
    def extractVolume( self, force_re=False ):
        print( self.cfg )
        if force_re == True: self.extr.recom_sphere = True
        self.data.extracted = self.extr( self.data.input, self.cfg.st_pt, self.cfg.dim_mults )
        self.data.modified[0] = True
        
        
    def extractSkeleton( self, use_extraction: bool, its=1, exp_mode="linear" ):
        if use_extraction:
            if self.data.extracted is not None:
                graph = self.skel( self.data.extracted, self.cfg.st_pt, self.cfg.dim_mults, its, exp_mode )
            else:
                raise Exception( "Extraction not computed!" )
        else:
            graph = self.skel( self.data.input, self.cfg.st_pt, self.cfg.dim_mults, its, exp_mode )
        self.data.modified[1] = True
        self.data.skeleton = graph
        
