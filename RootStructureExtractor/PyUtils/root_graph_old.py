#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from xml.etree import ElementTree as xml_et
from xml.dom import minidom
import vtk
import c_graph_interface as c_graph

def addAttr( name, val ):
    return " {0}=\"{1}\"".format( name, val )

class Node:
    @classmethod
    def fromCNode( cls, c_node_ptr ):
        #print("Node: {}".format(c_node_ptr.getRad()))
        c_node = c_graph.CGraphNode( c_node_ptr )
        node = cls( 0, c_node )
        node.initChildren()
        return node
    
    @classmethod
    def fromXml( cls, it, coor, rad, b_id ):
        c_node = c_graph.CGraphNode( 0 )
        node = cls( it, c_node )
        node.fillNode( coor, rad, b_id )
        return node
        
    
    def __init__( self, it, c_node ):
        print( "Init node" )
        self.c_node = c_node
        self.it = it
        self.children = []
        self.owner = True
        
        
    def __del__( self ):
        if self.owner:
            del self.c_node
        del self.children


    def update( self ):
        del self.children
        self.initChildren()

    def setOwner( self, is_owner ):
        self.owner = is_owner
        for child in self.children:
            child.setOwner( is_owner )

        
    def initChildren( self ): 
        self.children = []
        for child in self.c_node.getChildren(): 
            self.children.append( Node.fromCNode( child ) )
        
        
    def fillNode( self, coor, rad, branch_id ):
        self.setCoor( coor )
        self.setRad( rad )
        self.setBranchId( branch_id )
        
        
    def getCoor( self ): return self.c_node.getCoor()
    def getCoorAsFloat( self ):
        coors = self.c_node.getCoor()
        return [float(coors[0]), float(coors[1]), float(coors[2])]
    def setCoor( self, coor ): self.c_node.setCoor( coor )
    
    def getRad( self ): return self.c_node.getRad()
    def setRad( self, rad ): self.c_node.setRad( rad )
    
    def getBranchId( self ): return self.c_node.getBranchId()
    def setBranchId( self, b_id ): self.c_node.setBranchId( b_id )
    
    def getChildren( self ): return self.children
    def getChild( self, it ): return self.children[it]
        
        
    def appendNewNode( self, it, coor, rad, branch_id ):
        new_node = c_graph.CGraphNode( 0, False )
        self.fillNode( coor, rad, branch_id )
        self.c_node.append( new_node )
        self.children.append( Node( it, new_node ) )
        
    def append( self, node ):
        self.c_node.append( node.c_node )
        self.children.append( node )
        
    def appendCNode( self, c_node ):
        self.c_node.append( c_node )
        self.children.append( Node.fromCNode( c_node ) )

        
    def __str__( self ):
        out = "{0}: {1},{2} \n".format( self.it, self.getRad(), self.getCoor() )
        for child in self.getChildren():
            out += "  " +child.__str__()
        return out
    
    def size( self ):
        return self.c_node.rank()

    
    def addToVtk( self, points, edges, anchor=[0,0,0], mult=[1,1,1] ):
        coor = self.getCoor()
        p_coor = [ (coor[0] -anchor[0]) *mult[0], (coor[1] -anchor[1]) *mult[1], (coor[2] -anchor[2]) *mult[2] ]
        p_id = points.InsertNextPoint( p_coor[0], p_coor[1], p_coor[2] )
        for child in self.getChildren():
            line = vtk.vtkLine()
            line.GetPointIds().SetId( 0, p_id )
            line.GetPointIds().SetId( 1, child.addToVtk( points, edges, anchor, mult ) )
            edges.InsertNextCell( line )
        return p_id
    
    def addToVtkEval( self, points, edges, edges_wr, anchor=[0,0,0], mult=[1,1,1] ):
        coor = self.getCoor()
        p_coor = [ (coor[0] -anchor[0]) *mult[0], (coor[1] -anchor[1]) *mult[1], (coor[2] -anchor[2]) *mult[2] ]
        p_id = points.InsertNextPoint( p_coor[0], p_coor[1], p_coor[2] )            
        for child in self.getChildren():
            line = vtk.vtkLine()
            line.GetPointIds().SetId( 0, p_id )
            line.GetPointIds().SetId( 1, child.addToVtkEval( points, edges, edges_wr, anchor, mult ) )
            print( self.getRad() )
            if self.getRad() < 0.0:
                edges_wr.InsertNextCell( line )
            else:
                edges.InsertNextCell( line )
        return p_id
    
    def toXml( self ):
        xml_node = xml_et.Element( "Node" )
        xml_node.set( "id", str(self.it) )
        xml_node.set( "bo", str(self.getBranchId()) )
        xml_node.set( "rad", str(self.getRad()) )
        coor = self.getCoor()
        xml_node.set( "x", str(coor[0]) )
        xml_node.set( "y", str(coor[1]) )
        xml_node.set( "z", str(coor[2]) )
        for child in self.getChildren():
            xml_node.append( child.toXml() )
        return xml_node



class RootGraph:
    @classmethod
    def fromCGraph( cls, c_pointer ):
        base_graph = c_graph.CGraph( c_pointer )
        graph = cls()
        graph.graph_wrapper = base_graph
        #graph.root = Node.fromCNode( graph.graph_wrapper.getRoot() )
        return graph
    
    def __init__( self, f_name="" ):
        self.graph_wrapper = c_graph.CGraph( 0 )
        self.owner = True
        if f_name != "":
            self.fromXml( f_name )
            self.graph_wrapper.setRoot( self.root.c_node )
            self.root.c_node.setPtr( self.graph_wrapper.getRoot() )
            print(self.root.c_node.getCoor())
        else:
            self.root = Node( 0, 0 )

    def update( self ):
        print("update")
        self.setOwner( False )
        self.root.update()
        self.setOwner( True )
        print("dated")

    def setOwner( self, is_owner ):
        self.owner = is_owner
        self.root.setOwner( is_owner )

    def __del__( self ):
        if self.owner:
            del self.graph_wrapper
            
    def __str__( self ):
        return "{0}".format( self.getRoot() )
    
    def size( self ):
        return self.getRoot().size()
    
    def getNumberOfNodes( self ):
        return self.graph_wrapper.size()
    
    def getRoot( self ):
        return self.root


    def translate( self, offset3d ):
        self.graph_wrapper.translate( offset3d[0], offset3d[1], offset3d[2] )

    def translateTo( self, new_pos ):
        pos = self.root.c_node.getCoor()
        offset = ( new_pos[2]-pos[0], new_pos[1]-pos[1], new_pos[0]-pos[2] )
        self.translate( offset )

    def rotate( self, angles3d ):
        self.graph_wrapper.rotate( angles3d[0], angles3d[1], angles3d[2] )

    def evaluateRootID( self ):
        self.graph_wrapper.evaluateRootID()

    def repairRadius( self ):
        self.graph_wrapper.repairRadius()
    
    def fromXml( self, f_name ):
        xml_graph = xml_et.parse( f_name )
        xml_root = xml_graph.getroot()
        for child in xml_root:
            self.root = self.nodeFromXml( child )
        
        
    def nodeFromXml( self, xml_node ):
        it, rad, coor, br_id = self.valFromXml( xml_node )
        node = Node.fromXml( it, coor, rad, br_id )
        for child in xml_node:
            node.append( self.nodeFromXml( child ) )
        #node.initChildren()
        return node
        
    def valFromXml( self, xml_node ):
        coor = []
        it = int( xml_node.get( "id" ) )
        rad = float( xml_node.get( "rad" ) )
        br_id = int( xml_node.get( "bo" ) )
        coor.append( float( xml_node.get( "x" ) ) )
        coor.append( float( xml_node.get( "y" ) ) )
        coor.append( float( xml_node.get( "z" ) ) )
        return it, rad, coor, br_id
    
    def toXml( self, path ):
        root = xml_et.Element( "Forest" )
        root.append( self.getRoot().toXml() )
        xml_str = minidom.parseString( xml_et.tostring( root ) ).toprettyxml( indent="    " )
        with open( path, "w" ) as file:
            file.write( xml_str )
    
    
    def getVtkPolyData( self, mult=(1,1,1), anchor=None, gr_poly=None ):
        if gr_poly is None:
            gr_poly = vtk.vtkPolyData()
        vertex = vtk.vtkPoints()
        edges = vtk.vtkCellArray()
        if anchor is None:
            anchor = self.getRoot().getCoor()
        self.getRoot().addToVtk( vertex, edges, anchor, mult )
        
        gr_poly.SetPoints( vertex )
        gr_poly.SetLines( edges )
        gr_poly.Modified()
        
        return gr_poly
    
    def getVtkEvaluation( self, mult=(1,1,1), anchor=None ):
        gr_poly, wr_poly = vtk.vtkPolyData(), vtk.vtkPolyData()
        vertex = vtk.vtkPoints()
        edges = vtk.vtkCellArray()
        edges_wr = vtk.vtkCellArray()
        if anchor is None:
            anchor = self.getRoot().getCoor()
        self.getRoot().addToVtkEval( vertex, edges, edges_wr, anchor, mult )
        
        gr_poly.SetPoints( vertex )
        gr_poly.SetLines( edges )
        gr_poly.Modified()

        wr_poly.SetPoints( vertex )
        wr_poly.SetLines( edges_wr )
        wr_poly.Modified()      
        return gr_poly, wr_poly
    
    def toVtk( self, f_name, mult=(1,1,1), anchor=None ):
        gr_poly = self.getVtkPolyData( mult, anchor )
        writer = vtk.vtkXMLPolyDataWriter();
        writer.SetFileName( f_name );
        writer.SetInputData( gr_poly )
        writer.Write()
        
    def toVtkEvaluation( self, f_name, mult=(1,1,1), anchor=None ):
        gr_poly, wr_poly = self.getVtkEvaluation( mult, anchor )
        writer = vtk.vtkXMLPolyDataWriter();
        writer.SetFileName( f_name );
        writer.SetInputData( gr_poly )
        writer.Write()
        wr_name = "".join( f_name.split(".")[:-1] )
        writer.SetFileName( "{}_wr.vtp".format( wr_name ) )
        writer.SetInputData( wr_poly )
        writer.Write()
        
        
    def findPoint( self, pos ):
        def searchPoint( pos, node ):
            coor = node.getCoor()
            #print("{}=={}".format(pos, coor))
            if coor[0] == pos[0] and coor[1] == pos[1] and coor[2] == pos[2]:
                print("found")
                return node
            for child in node.getChildren():
                out = searchPoint( pos, child )
                if out is not None:
                    return out
            #print("not found")
            return None
        
        return searchPoint( pos, self.root )


    def getPointer( self ):
        return self.graph_wrapper.getPointer()

    def getDensePointList( self, mdist ):
        print("Get Points")
        return self.graph_wrapper.getDensePointList( mdist )

    def toVolume( self, dims ):
        return self.graph_wrapper.toVolume( dims )
        

if __name__ == "__main__":
    graph = RootGraph( "/home/jhorn/Documents/Work/PlantRootProject/plant-root-MRI-display/root_extraction/Data/downsampled_out_IV_Sand_3D_DAP8_128x128x96/root.xml" )
