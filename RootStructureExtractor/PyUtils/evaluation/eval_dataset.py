#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from xml.etree import ElementTree as xml_et
from xml.dom import minidom
import os
import numpy as np
from eval_graph import *
import root_graph
import eval_runner
import threading
import psutil

def pruneSegOutputName( fname ):
    st = "visualized_out_"
    ed_0 = "_uint8"
    ed_1 = "_mri"
    
    def deleteEnd0( out ):
        it = out.find("DAP")
        it = out.find("_", it)
        return out[:it]
    
    def deleteEnd1( out ):
        return out[:out.find( ed_1 )]
    
    out = fname
    if fname.find( st ) > -1:
        out = out[len(st):]
    if fname.find( ed_0 ) > -1:
        out = deleteEnd0( out )
    elif fname.find( ed_1 ) > -1:
        out = deleteEnd1( out )
    return out


def findName( flist, fname ):
    for f in flist:
        if f.find( fname ) > -1 and f.find( ".xml" ) > -1:
            return f
    raise OSError( "Could not locate ground truth .xml" )
            
    


class DatapointBase:
    
    def __init__( self, name, inp_path, gt_path ):
        try:
            self.findInputFile( name, inp_path )
            self.gt_path = os.path.join( gt_path, findName( os.listdir( gt_path ), name ) )
        except FileNotFoundError as e:
            raise e

    
    def findInputFile( self, name, inp_path ):
        self.path = None
        for file in os.listdir( inp_path ):
            path = os.path.join( inp_path, file )
            if os.path.isfile( path ):
                if file.find( name ) != -1 and file.find( ".npz" ):
                    self.path = os.path.join( inp_path, file )
                    break
        if self.path is None: raise FileNotFoundError( "No data path found for {0}!".format(name) )
        #self.path = inp_path +"visualized_out_" +name + "_"+ str(size)+ "x1x256x256_uint8/"
   
    
    def signatureXml( self, name ):
        el = xml_et.Element( name )
        i_el = xml_et.Element( "InputFile" )
        i_el.set( "path", self.path )
        o_el = xml_et.Element( "GtFile" )
        o_el.set( "path", self.gt_path )
        el.append( i_el )
        el.append( o_el )
        return el
  
    
    def __str__( self ):
        out = ""
        for dst, val in self.eval.items():
            out += "{}: {:.4}, {:.4}, {:.4}\n".format( dst, val[0], val[1], val[2] )
        return out


class Datapoint( DatapointBase ):

    def __init__( self, name, inp_path, gt_path ):
        try:
            super().__init__( name, inp_path, gt_path )
            self.it = 0
            root_gt = root_graph.RootGraph( self.gt_path )
            root_gt.toVtk( "{}/root_gt.vtp".format( self.path[:-4] ), [1/512,1/512, 1/512] )
        except FileNotFoundError as e:
            raise e


    def __call__( self, run_cfg, eval_cfg ):
        self.distances = eval_cfg["distances"]
        self.spacing = eval_cfg["spacing"]
        self.out = []
        self.time = {"lcc":0, "extr":0, "sum":0}
        self.mem = 0
        self.process = psutil.Process(os.getpid())
        eval_runner.runExtractionAndEvaluate( self, run_cfg )


    def evaluate( self, graph, param_cfg, times ):
        eval_vals = {}
        eval_params = param_cfg
        root_extracted = graph #root_graph.RootGraph.fromCGraph(graph)
        root_gt = root_graph.RootGraph(self.gt_path)
        print( "Loading root target from {}".format(self.gt_path) )
        #print( root_gt )
        graph.toVtk( "{}/root_{}.vtp".format( self.path[:-4], self.it  ), [1/512, 1/512, 1/512] )
        self.it += 1
        TPs = []
        for dst in self.distances:
            try:
                print( "{}: {}" .format( self.path, dst ) )
        
                root_point_list_extracted = dfs_tree(root_extracted.getRoot(), [], None, min_dist=self.spacing)
                root_point_list_extracted = np.array(root_point_list_extracted).astype(int)
                # print(root_point_list_extracted.astype(int).tolist()[:20])
        
                root_point_list_gt = dfs_tree(root_gt.getRoot(), [], None, min_dist=self.spacing)
                root_point_list_gt = np.array(root_point_list_gt).astype(int)
                # print(root_point_list_gt.astype(int).tolist()[:20])
        
                f1, pre, rec, TPs, GT_Fs = evaluate_extraction(root_point_list_extracted, root_point_list_gt, distance_thres=dst, spacing=self.spacing)
                #print("------\n{}\n------".format(TPs))
            except Exception as e:
                print( e )
                raise(e)
                f1, pre, rec = (0,0,0)
            print( "------" )
            self.f1 = f1
            self.pre = pre
            self.rec = rec
            eval_vals[str(dst)] = (f1, pre, rec)
        #for tp in TPs:
        #    may_node = root_extracted.findPoint( tp )
        #    if may_node is not None:
        #        may_node.setRad(-1.0)
        #print( "\n----\nGT_Fs:{}\n----".format( len(GT_Fs) ) )
        #for gt_f in GT_Fs:
        #    may_node = root_gt.findPoint( gt_f )
        #    if may_node is not None:
        #        may_node.setRad(-1.0)
        #print( root_gt )
                
        self.time["lcc"] = times[0]
        self.time["extr"] = times[1]
        self.time["sum"] = times[2]
        print(self.time)
        self.mem = self.process.memory_info().rss
        
        #print( "\n-----\nRootEval: {}\n-----".format(self.path[:-4]) )
        #root_extracted.toVtkEvaluation( "{}/root_eval_{}.vtp".format( self.path[:-4], self.it ), [1/512, 1/512, 1/512] )
        #root_gt.toVtkEvaluation( "{}/gt_eval_{}.vtp".format( self.path[:-4], self.it ), [1/512, 1/512, 1/512] )
        del root_gt
        del root_extracted
        #del TPs
        #del GT_Fs
        self.out.append( (eval_params, eval_vals) )


    def toXml( self, name ):
        def toXmlStr( val, prec=4 ):
            if isinstance( val, float ): return "{:.{pr}f}".format( val, pr=prec )
            if isinstance( val, int ): return "{}".format(val)
            return "{:.{pr}}".format( val, pr=prec )
        
        b_el = xml_et.Element( name )
        for params, vals in self.out:
            el = xml_et.Element( "Params" )
            el.set( "cutoff", toXmlStr( params["ct"], 2 ) )
            el.set( "glength", toXmlStr( params["gl"], 0 ) )
            el.set( "dil_sum", toXmlStr( float(params["ds"])/100, 2 ) )
            el.set( "num_its", toXmlStr( params["ni"], 0 ) )
            el.set( "intp", toXmlStr( float(params["it"]), 2 ) )
            for dst, val in vals.items():
                dst_el = xml_et.Element( "val" )
                dst_el.set( "dst", str(dst) )
                dst_el.set( "f1", toXmlStr( val[0] ) )
                dst_el.set( "rec", toXmlStr( val[1] ) )
                dst_el.set( "pre", toXmlStr( val[2] ) )
                el.append( dst_el )
            b_el.append( el )
        t_el = xml_et.Element( "Time" )
        t_el.set( "lcc", toXmlStr( toXmlStr( self.time["lcc"], 6 ) ) )
        t_el.set( "extr", toXmlStr( toXmlStr( self.time["extr"], 6 ) ) )
        t_el.set( "sum", toXmlStr( toXmlStr( self.time["sum"], 6 ) ) )
        b_el.append( t_el )
        m_el = xml_et.Element( "Memory" )
        m_el.set( "usage", toXmlStr( self.mem, 0 ) )
        b_el.append( m_el )
        return b_el


class XmlDatapoint( DatapointBase ):

    def __init__( self, xml_node, inp_path, gt_path ):
        super().__init__( xml_node.tag, inp_path, gt_path )
        print(xml_node)
        self.xml = xml_node
       
    def __call__( self, run_cfg, eval_cfg ):
        pass

    def toXml( self, name ):
        return self.xml


class OutputHandler:
    
    def __init__( self, func_write, lock ):
        self.run = True
        self.save = False
        self.lock = lock
        self.cond = threading.Condition()
        self.thread = threading.Thread( target=self.write, args=[func_write] )
        self.thread.start()
        
    def write( self, func_write ):
        while( self.run ):
            with self.cond:
                while not self.save:
                    self.cond.wait()
                self.lock.acquire()
                print( "Saving..."+str(self.run) )
                func_write()
                self.save = False
                self.lock.release()
            
    def __call__( self ):
        with self.cond:
            self.save = True
            self.cond.notify_all()
        
    def stop( self ):
        with self.cond:
            self.run = False
            self.cond.notify_all()
        self.thread.join()
    

class Dataset:
    
    def __init__( self, base_path, gt_path, out_path, load=True ):
        self.base_path = base_path
        self.gt_path = gt_path
        self.dt = {}
        self.eval = {}
        self.xml_out = xml_et.Element( "RootEvalSet" )
        self.lock = threading.Lock()
        self.out_lock = threading.Lock()
        self.output = OutputHandler( self.saveSet, self.out_lock )
        self.out = out_path
        self.contains = {}
        if load:
            path = "{}../{}_temp.xml".format( self.base_path, self.out )
            if os.path.isfile( path ): self.loadOutXml(path)
            else: print( "{} is no File!".format(path) )
          
    def loadOutXml( self, path ):
        xml_root = xml_et.parse( path ).getroot()
        for child in xml_root:
            if child.tag != "Signature":
                self.contains[child.tag] = child
        print( "Got following tags: {}".format(self.contains) )
    
    def build( self ):
        for fname in os.listdir( self.base_path ):
            if fname.find( ".npz" ) > -1 or fname.find( ".npy" ) > -1:
                self.add( pruneSegOutputName( fname ) )
        s_el = xml_et.Element( "Signature" )
        for key, dt in self.dt.items():
            s_el.append( dt.signatureXml(key) )
        self.xml_out.append( s_el )
        self.save( "signature.xml" )

    def add( self, name ):
        try:
            if name not in self.contains.keys():
                self.dt[name] = Datapoint( name, self.base_path, self.gt_path )
            else: 
                self.dt[name] = XmlDatapoint( self.contains[name], self.base_path, self.gt_path )
                print( "\n\n==================\n{} already evaluated.\n==================\n\n".format(name) )
        except OSError:
            self.dt.pop( name, None )
            print( "Could not find foulder for {0}".format( name ) )
        
    def save( self, f_name ):
        #print(xml_et.tostring( self.xml_out ))
        xml_str = minidom.parseString( xml_et.tostring( self.xml_out ) )
        xml_nopretty = ''.join([line.strip() for line in xml_str.toxml().splitlines()])
        xml_str = minidom.parseString( xml_nopretty ).toprettyxml( indent="    " )
        with open( self.base_path +"../" +f_name, "w" ) as file:
            file.write( xml_str )
            
    def saveSet( self ):
        self.save( "{}_temp.xml".format( self.out ) )
        
    def getIterator( self ):
        self.lock.acquire()
        if self.it < len( self.dt ):
            it = self.it
            self.it += 1
        else:
            it = -1
        self.lock.release()
        print(it)
        return it
        
    def appendVals( self, key, dtp ):
        self.out_lock.acquire()
        self.xml_out.append( dtp.toXml(key) )
        self.out_lock.release()
        self.output()

    
    def __call__( self, run_cfg, eval_cfg, num_threads ):
        self.it = 0
        self.temp_list = list( self.dt.items() )
        threads = []
        for i in range( num_threads ):
            thread = threading.Thread( target=self.threadFunction, args=(run_cfg, eval_cfg) )
            threads.append( thread )
            thread.start()
        for thread in threads:
            thread.join()
        self.save( "{}.xml".format( self.out ) )
        print( "\n-----\nEvaluation done!\n-----" )
        self.output.stop()

            
    def threadFunction( self, run_cfg, eval_cfg ):
        #print( "{0}:".format(key) )
        it = self.getIterator()
        while( it >= 0 ):
            key, dtp = self.temp_list[it]
            print( "Evaluating {0}".format(key) )
            dtp( run_cfg, eval_cfg )
            self.appendVals( key, dtp )
            it = self.getIterator()

    def __str__( self ):
        out = "Eval Dataset: \n"
        for key in self.dt.keys():
            out += "  {0} \n".format( key )
        return out
            
