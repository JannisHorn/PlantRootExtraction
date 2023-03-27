#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import os
import numpy as np
import root_graph as rg
import xml.etree.ElementTree as et
import root_graph_to_dgf as dgf
from xml.dom import minidom

class DataFile:
    def __init__( self, data_path: str ):
        self.default()
        self.setPath( data_path )
        self.is_file = True
        self.is_npy = True
        
    @classmethod
    def defaultFile( nfile, path: str ):
        nfile.default()
        return nfile
        
    def default( self ):
        self.config_name = "config.xml"
        self.extracted_name = "extracted.npz"
        self.skeleton_name = "skeleton.npz"
        self.xml_name = "root.xml"
        self.vtk_name = "root.vtp"
        self.dgf_name = "root.dgf"
        self.bstats_name = "branch_stats.csv"
        self.nstats_name = "node_stats.csv"

    def setPath( self, data_path: str ):
        self.path = data_path
        file_strs = self.path.split("/")
        self.file_name = file_strs[-1].split(".")[0]
        self.save_path = "/".join( file_strs[:-1] ) +"/" +self.file_name +"/"
        self.folder_path = "/".join( file_strs[:-1] )
        print( "Set current file to: {0}".format( self.path ) )
        
    def __str__( self ):
        return self.file_name


    @classmethod
    def loadFile( self, path: str ):
        try:
            if path[-4:] == ".npz":
                data = np.load( path )["arr_0"]
                print( "Load from .npz Archive" )
            else:
                data = np.load( path )
            data = data.astype( np.float32 )
            data /= data.max()
            data = np.squeeze( data )
            return data
        except (IOError, ValueError) as e:
            raise e
     
    @classmethod
    def loadCfg( self, path_cfg: str ):
        def xmlToDic( xml_cfg ):
            out = {}
            for child in xml_cfg:
                out[child.tag] = child.attrib
            for key, val in xml_cfg.attrib.items():
                out[key] = val
            return out
        
        try:
            cfgs = [None, None, None]
            xml_cfg = et.parse( path_cfg )
            xml_root = xml_cfg.getroot()
            errs = [None, None, None]
            for child in xml_root:
                try:
                    if child.tag == "Input":
                        print("    Loading Input config")
                        cfgs[0] = xmlToDic(child)
                except KeyError as e: errs[0] = e
                try:
                    if child.tag == "Extraction":
                        print("    Loading Extraction config")
                        cfgs[1] = xmlToDic(child)
                except KeyError as e: errs[1] = e
                try:
                    if child.tag == "Skeletonization":
                        print("    Loading Skeleton config")
                        cfgs[2] = xmlToDic(child)
                except KeyError as e: errs[2] = e
                err_str = "KeyError in Loading Config: "
                if errs[0] is not None: err_str.append( "Input: {}".format(errs[0]) )
                if errs[1] is not None: err_str.append( "Extr: {}".format(errs[1]) )
                if errs[2] is not None: err_str.append( "Skel: {}".format(errs[2]) )
                if any(errs): print( err_str )
            return cfgs
        except Exception as e:
            raise e
        
    def loadArchive( self ):
        try:
            out = [None,None,None]
            cfg = [None,None,None]
            path_cfg = os.path.join( self.save_path, self.config_name )
            path_inp = self.path
            path_extr = os.path.join( self.save_path, self.extracted_name )
            path_skel = os.path.join( self.save_path, self.xml_name )

            if os.path.isfile( path_cfg ):
                print( "Loading config {0}".format( path_cfg ) )
                cfg = self.loadCfg( path_cfg )
            if os.path.isfile( path_inp ):
                print("Loading input {0}".format(path_inp))
                out[0] = self.loadFile( path_inp )
            if os.path.isfile( path_extr ):
                print("Loading extracted volume {0}".format(path_extr))
                out[1] = self.loadFile( path_extr )
            if os.path.isfile( path_skel ):
                print("Loading root graph {0}".format(path_skel))
                out[2] = rg.RootGraph( path_skel )

            return cfg, out
        
        except Exception as e:
            print( "{0}: Error in loading Archove {1}".format( __name__, self.path ) )
            raise e
    
    def load( self ):
        """ Top level loader: Either loads single file or archive if dir with same name as input exists """
        try:
            if os.path.isdir( self.save_path ):
                return self.loadArchive()
            else:
                out = self.loadFile( self.path )
                print( "Loading: \"{0}\"".format( self.path ) )
                return [None,None,None], [out, None, None]
        except (IOError, ValueError) as e:
            print( "{0}: Error in loading {1}".format( __name__, self.path ) )
            raise IOError( "Error while loading file: {}".format(e) )
            
    def importFile( self, fname: str, dt_cfg ):
        try:
            out = dt_cfg.importFile( fname )
            self.is_npy = False
            print( "Loading: \"{0}\"".format( fname ) )
            self.file_name = dt_cfg.data_name
            print(self.file_name)
            self.saveInput( out )
            return [out, None, None]
        except (IOError, ValueError) as e:
            print( "{0}: Error in loading {1}".format( __name__, fname ) )
            raise IOError(str(e))

    def loadGraph( self, fname: str ):
        try:
            path_from_npy = os.path.join( fname[:-4], self.xml_name )
            if os.path.isfile( path_from_npy ) and fname[-3:] != "xml":
                print( "Trying to load {}".format( path_from_npy ) )
                return rg.RootGraph( path_skel )
            else:
                print( "Trying to load {}".format( fname ) )
                return rg.RootGraph( fname )
        except (IOError, ValueError, et.ParseError) as e:
            print( "{0}: Error in loading {1}".format( __name__, fname ) )
            raise IOError(str(e))

            
    def saveInput( self, inp ):
        print( "Saving input numpy to {}".format( os.path.join( self.folder_path, self.file_name ) ) )
        file_path = os.path.join( self.folder_path, self.file_name )
        np.savez( file_path, inp )
        self.setPath( "{}.npz".format(file_path) )
        self.is_npy = True
        

          
    def save( self, fname: str, data: np.array, data_cfg, ecfg, scfg ):
        """ Contructs directory based on file name and saves extraction, graph and config if applicable"""
        def from3DList( root, name, l ):
            elem = et.SubElement( root, name )
            elem.set( "x", str(l[0]) )
            elem.set( "y", str(l[1]) )
            elem.set( "z", str(l[2]) )
        
        def dataCfgToXml():
            xml_cfg = et.Element( "Input" )
            for key, val in data_cfg.toItems().items():
                if key in ["StartPos", "DimMults"]:
                    from3DList( xml_cfg, key, val )
                else:
                    xml_cfg.set( key, str(val) )
            return xml_cfg
        
        def extrCfgToXml():
            xml_cfg = et.Element( "Extraction" )
            for key, val in ecfg.toItems().items():
                xml_tp = et.SubElement( xml_cfg, key )
                for key_i, val_i in val.items():
                    xml_tp.set( key_i, str(val_i) )
            return xml_cfg
        
        def skelCfgToXml():
            xml_cfg = et.Element( "Skeletonization" )
            for key, val in scfg.toItems().items():
                xml_cfg.set( key, str(val) )
            return xml_cfg
        
        def saveInput():
            print( "Saving input numpy to {}".format( os.path.join( self.folder_path, self.file_name ) ) )
            file_path = os.path.join( self.folder_path, self.file_name )
            np.savez( file_path, data.input )
            self.setPath( file_path )
            self.is_npy = True
        
        def saveExtr():
            if data.modified[0]:
                np.savez( self.save_path +self.extracted_name, data.extracted )
                print( "Saved extracted volume to {0}".format( self.save_path +self.extracted_name ) )
            xml_extr = extrCfgToXml()
            xml_root.append( xml_extr )
            
        def saveGraph( min_age, max_age, max_type, vox_res ):
            if data.modified[1]:
                data.skeleton.toXml( self.save_path +self.xml_name )
                print( "Saved extracted graph to {0}".format( self.save_path +self.xml_name ) )
                mults = data_cfg.dim_mults
                st_pt = data_cfg.st_pt /data.input.shape[2]
                res_mults = [x*vox_res/2000 for x in mults]
                res_mults.reverse()
                print( "Graph mults: {} -> {}".format( mults, res_mults ) )
                data.skeleton.toVtk( self.save_path +self.vtk_name, res_mults )
                print( "Saved vtk to {0}".format( self.save_path +self.vtk_name ) )
                dgf.graph_to_dgf( data.skeleton, min_age, max_age, max_type, self.save_path +self.dgf_name, vox_res, mults )
                print( "Saved dgf to {0}".format( self.save_path +self.dgf_name ) )
                data.skeleton.saveBranchStatistics( self.save_path +self.bstats_name )
                print( "Saved stats to {0}".format( self.save_path +self.bstats_name ) )
                data.skeleton.saveNodeStatistics( self.save_path +self.nstats_name )
                print( "Saved Node stats to {0}".format( self.save_path +self.nstats_name ) )
            xml_root.append( skelCfgToXml() )
        
        try:
            if fname != "":
                self.save_path = fname
                self.is_npy = False
            if not os.path.exists( self.save_path ):
                print( "Creating directory {0}".format( self.save_path ) )
                os.mkdir( self.save_path )
            xml_root = et.Element("Config")
            xml_cfg = et.ElementTree( xml_root )
            xml_data = dataCfgToXml()
            xml_root.append( xml_data )
            
            if not self.is_npy:
                saveInput()
            
            if data.extracted is not None:
                saveExtr()
                
            if data.skeleton is not None:
                saveGraph( data_cfg.ages[0], data_cfg.ages[1], data_cfg.max_type, data_cfg.vox_res )
            
            xml_str = minidom.parseString(et.tostring(xml_root)).toprettyxml(indent="   ")
            with open( os.path.join( self.save_path, self.config_name ), "w" ) as file:
                file.write( xml_str )
        except IOError as e:
            raise e

    def saveGraphAsXml( self, fname:str, data ):
        dataname = fname
        if dataname[-4:] != ".xml":
            dataname += ".xml"
        print( "Saving graph to {}".format( dataname ) )
        data.skeleton.toXml( dataname )
