#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore, QtGui

class DataTreeWidget( qtw.QWidget ):
    
    def __init__( self, parent, name ):
        super().__init__( parent )
        self.data_tree_view = parent.findChild( qtw.QTreeWidget, name )
        self.data_tree_view.setHeaderItem( qtw.QTreeWidgetItem( ["Data Structure","Value"] ) )
        self.data_tree_view.setColumnWidth( 0, 150 )
        
    def updateTreeView( self, data_cstr ):
        def interpretItem( root, key, val ):
            if isinstance( val, dict ):
                new_item = qtw.QTreeWidgetItem( root, [key] )
                self.data_tree_items.append( new_item )
                for key, value in val.items():
                    interpretItem( new_item, key, value )
            else:
                new_item = qtw.QTreeWidgetItem( root, [key] )
                new_item.setText( 1, str(val) )
                new_item.setIcon( 0, self.style().standardIcon(getattr(qtw.QStyle, "SP_FileDialogInfoView" ) ))
                self.data_tree_items.append( new_item )
        
        
        def dataMissing( node ):
            def grayNode( node ):
                node.setForeground( 0, QtCore.Qt.gray )
                node.setForeground( 1, QtCore.Qt.gray )
                font = QtGui.QFont()
                font.setItalic(True)
                node.setFont( 0, font )
                node.setFont( 1, font )
                ch_ct = node.childCount()
                if ch_ct == 0:
                    node.setIcon( 0, self.style().standardIcon(getattr(qtw.QStyle, "SP_MessageBoxWarning" ) ))
                else:
                    for ch_it in range( ch_ct ):
                        grayNode( node.child(ch_it) )
            
            node.setText(1, "No Data")
            font = QtGui.QFont()
            font.setBold(True)
            node.setFont( 1, font )
            node.setIcon(1, self.style().standardIcon(getattr(qtw.QStyle, "SP_MessageBoxCritical" ) ) )
            for ch_it in range( node.childCount() ):
                grayNode( node.child(ch_it) )
                
                
        def dataModifed( mods ):
            def ptModified( node ):
                node.setText( 1, "Unsaved Changes" )
                font = QtGui.QFont()
                font.setBold(True)
                node.setFont( 1, font )
                node.setIcon( 1, self.style().standardIcon(getattr(qtw.QStyle, "SP_MessageBoxWarning" ) ))
                
            if mods[0] and self.data_tree_view.itemAt(0,0).childCount() > 1:
                ptModified( self.data_tree_view.itemAt(0,0).child( 1 ) )
            if mods[1] and self.data_tree_view.itemAt(0,0).childCount() > 2:
                ptModified( self.data_tree_view.itemAt(0,0).child( 2 ) )
                
                
        self.data_tree_view.clear()
        stats = data_cstr.getStatus()
        if stats is not None and data_cstr.valid():
            self.view_name = qtw.QTreeWidgetItem( stats.name )
            self.data_tree_view.addTopLevelItem( self.view_name )
            self.data_tree_items = []
            it = 0
            for key, val in stats.items.items():
                interpretItem( self.view_name, key, val )
                if not stats.has_data[it]:
                    dataMissing( self.data_tree_view.itemAt(0,0).child( it ) )
                it += 1
            dataModifed( data_cstr.data.modified )
            self.data_tree_view.expandToDepth(2)
