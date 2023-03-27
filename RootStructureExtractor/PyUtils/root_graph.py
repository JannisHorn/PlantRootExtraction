#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""
import math
from xml.etree import ElementTree as xml_et
from xml.dom import minidom
import vtk
import c_graph_interface as c_graph
import csv

def addAttr( name, val ):
    return " {0}=\"{1}\"".format( name, val )

"""
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
"""


class RootGraph:
    @classmethod
    def fromCGraph( cls, c_pointer ):
        base_graph = c_graph.CGraph( c_pointer )
        print( c_pointer, c_graph.CGraphNode( base_graph.getRoot() ).getCoor() )
        graph = cls()
        graph.graph_wrapper = base_graph
        graph.root = c_graph.CGraphNode( base_graph.getRoot() )
        print( graph.root.getCoor() )
        return graph
    
    def __init__( self, f_name="" ):
        self.graph_wrapper = c_graph.CGraph( 0 )
        self.owner = True
        if f_name != "":
            self.fromXml( f_name )
            self.graph_wrapper.setRoot( self.root )
            self.root = c_graph.CGraphNode( self.graph_wrapper.getRoot() )
            #self.root.c_node.setPtr( self.graph_wrapper.getRoot() )
        else:
            self.root = c_graph.CGraphNode( 0 )

    def setOwner( self, is_owner ):
        self.graph_wrapper.setOwnership( is_owner )

    #def __del__( self ):
    #    if self.owner:
    #        del self.graph_wrapper
            
    def __str__( self ):
        return "{0}".format( self.getRoot() )
    
    def size( self ):
        return self.getRoot().size()
    
    def getNumberOfNodes( self ):
        return self.graph_wrapper.size()
    
    def getRoot( self ):
        return self.root

    def getPointer( self ):
        return self.graph_wrapper.getPointer()


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

    def repairPreds( self ):
        self.graph_wrapper.repairPreds()

    def repairTips( self ):
        self.graph_wrapper.repairTips()
    
    def fromXml( self, f_name ):
        xml_graph = xml_et.parse( f_name )
        xml_root = xml_graph.getroot()
        for child in xml_root:
            self.root = self.nodeFromXml( child )
            print(self.root.getPtr(), self.root.getCoor())

        
    def valFromXml( self, xml_node ):
        coor = []
        br_id = int( xml_node.get( "id" ) )
        rad = float( xml_node.get( "rad" ) )
        it = int( xml_node.get( "bo" ) )
        coor.append( float( xml_node.get( "x" ) ) )
        coor.append( float( xml_node.get( "y" ) ) )
        coor.append( float( xml_node.get( "z" ) ) )
        return it, rad, coor, br_id
    
    def toXml( self, path ):
        root = xml_et.Element( "Forest" )
        root.append( self.nodeToXml( self.getRoot() ) )
        xml_str = minidom.parseString( xml_et.tostring( root ) ).toprettyxml( indent="    " )
        with open( path, "w" ) as file:
            file.write( xml_str )

    def nodeToXml(self, cur_node):
        xml_node = xml_et.Element("Node")
        xml_node.set("id", str(cur_node.getBranchId()))
        xml_node.set("bo", str(0))
        xml_node.set("rad", str(cur_node.getRad()))
        coor = cur_node.getCoor()
        xml_node.set("x", str(coor[0]))
        xml_node.set("y", str(coor[1]))
        xml_node.set("z", str(coor[2]))
        for child in cur_node.getChildren():
            xml_node.append( self.nodeToXml( c_graph.CGraphNode( child ) ) )
        return xml_node


    def nodeFromXml( self, xml_node ):
        it, rad, coor, br_id = self.valFromXml( xml_node )
        node = c_graph.CGraphNode( 0 )
        node.setCoor( coor )
        node.setRad( rad )
        node.setBranchId( br_id )
        for child in xml_node:
            ptr = self.nodeFromXml( child )
            node.append( ptr )
        return node
    
    
    def getVtkPolyData( self, mult, anchor=None, gr_poly=None ):
        print( "To vtp using multiplier: {}".format( mult ) )
        if gr_poly is None:
            gr_poly = vtk.vtkPolyData()
        vertex = vtk.vtkPoints()
        edges = vtk.vtkCellArray()
        radius = vtk.vtkDoubleArray()
        radius.SetName( "Radius" )
        orders = vtk.vtkDoubleArray()
        orders.SetName("RootOrder")
        if anchor is None:
            anchor = self.getRoot().getCoor()
        self.addNodeToVtk( self.getRoot(), vertex, edges, radius, orders, 0, 0, anchor, mult )
        
        gr_poly.SetPoints( vertex )
        gr_poly.GetPointData().SetScalars( radius )
        gr_poly.GetPointData().AddArray( orders )
        gr_poly.SetLines( edges )
        gr_poly.Modified()
        
        return gr_poly
    
    def toVtk( self, f_name, mult, anchor=None ):
        gr_poly = self.getVtkPolyData( mult, anchor )
        writer = vtk.vtkXMLPolyDataWriter();
        writer.SetFileName( f_name );
        writer.SetInputData( gr_poly )
        writer.Write()

    def addNodeToVtk(self, cur_node, points, edges, radius, orders, last_id, last_order, anchor, mult):
        coor = cur_node.getCoor()
        p_coor = [(coor[0] - anchor[0]) * mult[0], (coor[1] - anchor[1]) * mult[1], (coor[2] - anchor[2]) * mult[2]]
        p_id = points.InsertNextPoint(p_coor[0], p_coor[1], p_coor[2])
        id = cur_node.getBranchId()
        if id == last_id: order = last_order
        else: order = last_order+1
        radius.InsertNextValue( cur_node.getRad() )
        orders.InsertNextValue( order )
        for child in cur_node:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, p_id)
            line.GetPointIds().SetId(1, self.addNodeToVtk(c_graph.CGraphNode( child ), points, edges, radius, orders, id, order, anchor, mult))
            edges.InsertNextCell(line)
        return p_id


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

    def getVtkEvaluation(self, mult=(1, 1, 1), anchor=None):
        gr_poly, wr_poly = vtk.vtkPolyData(), vtk.vtkPolyData()
        vertex = vtk.vtkPoints()
        edges = vtk.vtkCellArray()
        edges_wr = vtk.vtkCellArray()
        if anchor is None:
            anchor = self.getRoot().getCoor()
        self.addNodeToVtkEval(self.root, vertex, edges, edges_wr, anchor, mult)

        gr_poly.SetPoints(vertex)
        gr_poly.SetLines(edges)
        gr_poly.Modified()

        wr_poly.SetPoints(vertex)
        wr_poly.SetLines(edges_wr)
        wr_poly.Modified()
        return gr_poly, wr_poly

    def addNodeToVtkEval(self, cur_node, points, edges, edges_wr, anchor=[0, 0, 0], mult=[1, 1, 1]):
        coor = cur_node.getCoor()
        p_coor = [(coor[0] - anchor[0]) * mult[0], (coor[1] - anchor[1]) * mult[1], (coor[2] - anchor[2]) * mult[2]]
        p_id = points.InsertNextPoint(p_coor[0], p_coor[1], p_coor[2])
        for child in cur_node:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, p_id)
            line.GetPointIds().SetId(1, self.addNodeToVtkEval(c_graph.CGraphNode( child ), points, edges, edges_wr, anchor, mult))
            print(cur_node.getRad())
            if cur_node.getRad() < 0.0:
                edges_wr.InsertNextCell(line)
            else:
                edges.InsertNextCell(line)
        return p_id

        
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


    def getDensePointList( self, mdist ):
        print("Get Points")
        return self.graph_wrapper.getDensePointList( mdist )

    def toVolume( self, dims ):
        return self.graph_wrapper.toVolume( dims )


    def getBranchStatistics( self ):
        stats = []
        self.getBranchStatsBranch( stats, self.getRoot() )
        return stats

    def getBranchStatsBranch( self, stats, root_node ):
        length = 0
        vol = 0
        radii = []
        while len(root_node) > 0:
            cur_node = root_node
            root_node = c_graph.CGraphNode(root_node[0])
            cur_len = self.nodeDist(cur_node, root_node)
            length += cur_len
            vol += self.nodeVol( cur_node, root_node, cur_len )
            radii.append( cur_node.getRad() )
            for c_it in range(1, len(cur_node)):
                self.getBranchStatsBranch( stats, c_graph.CGraphNode(cur_node[c_it]) )
        if length > 0:
            stats.append( (length, vol, radii) )

    def saveBranchStatistics( self, path = "branchs.csv" ):
        stats = self.getBranchStatistics()
        with open( path, 'w' ) as bf:
            bf.write( "Length, Volume, Radii\n" )
            for stat in stats:
                bf.write( str(stat[0]) +', ' )
                bf.write( str(stat[1]) +', ' )
                rad_str = ""
                for rad in stat[2]:
                    rad_str += "{}, ".format( rad )
                bf.write( rad_str +"\n" )


    def getNodeStatistics( self ):
        stats = []
        self.getNodeStatsNode( stats, self.getRoot() )
        return stats

    def getNodeStatsNode( self, stats, node ):
        stats.append( [node.getBranchId(), node.getRad(), len(node)] )
        for child in node:
            self.getNodeStatsNode( stats, c_graph.CGraphNode(child) )

    def saveNodeStatistics( self, path = "nodes.csv" ):
        stats = self.getNodeStatistics()
        with open( path, 'w' ) as nf:
            nf.write( "Id, Radius, Rank\n" )
            for stat in stats:
                nf.write( "{0}, {1}, {2}\n".format( stat[0], stat[1], stat[2] ) )


    def nodeDist( self, node0, node1 ):
        pos0 = node0.getCoor()
        pos1 = node1.getCoor()
        sqrd_dist = (pos1[0] -pos0[0])**2
        sqrd_dist += (pos1[1] -pos0[1])**2
        sqrd_dist += (pos1[2] -pos0[2])**2
        return math.sqrt( sqrd_dist )

    def nodeVol( self, node0, node1, dist ):
        r0 = node0.getRad()
        r1 = node1.getRad()
        return 1/3*math.pi*(r0**2 +r0*r1 +r1**2) *dist


if __name__ == "__main__":
    graph = RootGraph( "/home/jhorn/Documents/Work/PlantRootProject/plant-root-MRI-display/root_extraction/Data/downsampled_out_IV_Sand_3D_DAP8_128x128x96/root.xml" )
    #print(graph)
    print("Done")
    print( graph.root )
    print(graph.root[0])
