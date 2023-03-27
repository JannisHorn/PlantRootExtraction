#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk_actor_pipe as vtk_actor
import vtk_data_container as vtk_data
import vtk_custom_interactor as vtk_ci
import vtk_render_windows as vtk_wins

class RenderWindowSlotBase:
    def __init__( self, win ):
        self.window = win

    
    def __call__( self ):
        return self.window
            
            
    def SetAsActive( self ):
        self.window.SetAsActive()
            
            
            
class RenderWindowSlot( RenderWindowSlotBase ):
    def __init__( self, win ):
        super().__init__( win )
        self.actors = dict()
        
        
    def FromActor( self, data_name, data, actor_type ):
        if not data_name in self.actors:
            actor = actor_type()
            actor.SetInputData( data )
            self.window.AddActor( actor )
            self.actors[data_name] = actor
            print( self.actors )
        else:
            data.Modified()
        return self.actors[data_name]
    
    
    def DelActor( self, data_name ):
        if data_name in self.actors:
            self.window.RemoveActor( self.actors[data_name] )
            del self.actors[data_name]
            
    
    def GetActor( self, data_name ):
        if data_name in self.actors:
            return self.actors[data_name]
        else:
            return None
    
    
    def Clear( self ):
        #for data_name, actor in self.actors.items():
        #    self.window.RemoveActor( actor )
        self.window.Reset()
        self.actors.clear()
    
    
    def Update( self ):
        for data_name, actor in self.actors.items():
            actor.Update()
    
    
    
class RenderWindowSlotExclusive( RenderWindowSlotBase ):
    def __init__( self, win ):
        super().__init__( win )
        self.actor = None
        self.data_name = ""
    

    def FromActor( self, data_name, data, actor_type ):
        if not data_name == self.data_name:
            actor = actor_type()
            actor.SetInputData( data )
            self.window.AddActor( actor )
            self.actor = actor
            self.data_name = data_name
        else:
            self.actor.GetInput().Modified()
        return self.actor
    
    
    def DelActor( self, data_name ):
        if data_name == self.data_name:
            self.window.RemoveActor( self.actor )
            self.actor = None
            
            
    def GetActor( self, data_name ):
        if data_name == self.data_name:
            return self.actor
        else:
            return None
        
    
    def Clear( self ):
        if self.actor is not None:
            self.window.RemoveActor( self.actor )
            self.actor = None
        
        
    def Update( self ):
        if self.actor is not None:
            self.actor.Update()



class vtkWindowInteractor( QVTKRenderWindowInteractor ):
    
    def __init__( self, parent, dt_s ):
        QVTKRenderWindowInteractor.__init__(self, parent)
        self.rend_crt = vtk_ci.vtkInteractorStyleController( self )
        self.AddObserver( "MouseMoveEvent", self.rend_crt )
        self.window = self.GetRenderWindow()
        
        self.data = vtk_data.vtkDataCollection(dt_s)
        self.slots = list()
        self.active_actor = None
        self.slots.append( RenderWindowSlot( vtk_wins.vtkVolumeWindow( self.window ) ) )
        self.slots.append( RenderWindowSlotExclusive( vtk_wins.vtkVolumeSliceWindow( self.window ) ) )
        self.SetActiveWindow( 0 )
        self.win_inter = self.GetInteractor()
        
        
    def ConnectToVolCrtWidget( self, widg ):
        widg.addButtonPressed.connect( self.AddActor )
        widg.delButtonPressed.connect( self.DelActor )
        widg.connectActVis( self.SetVisibility )
        widg.connectActFore( self.SetForeground )
        widg.connectActColor( self.SetColor )
        widg.connectActOpac( self.SetOpacity )
        widg.connectActThresh( self.SetThreshold )
        widg.itemChangedText.connect( self.SetCurrentActor )
        self.fillWidg = widg.fillFromParams
        
    def ConnectToSliceCrtWidget( self, widg ):
        widg.addButtonPressed.connect( self.AddActor )
        widg.connectActThresh( self.SetThreshold )
        
        
        
    def SetActiveWindow( self, it ):
        print( "Current Active Renwin: {0}".format(it) )
        self.active_renwin = self.slots[it]
        self.active_renwin.SetAsActive()
        self.Render()
        
        
    def GetActiveWindow( self ):
        return self.active_renwin()
    
    
    def AddRenderer( self, ren ):
        self.active_renwin().AddRenderer( ren )
    
    def AddRendereToWindow( self, ren, it ):
        self.renwins[it]().AddRenderer( ren )
        
        
    def RemoveRenderer( self, ren ):
        self.active_renwin().RemoveRenderer( ren )
        
    def RemoveRendererFromWindow( self, ren, it ):
        self.renwins[it]().RemoveRenderer( ren )
    
    
    def GetInteractor( self ):
        return self.active_renwin().GetInteractor()
        
    
    def AddActor( self, data_name ):
        data = None
        if data_name in self.data.GetImageKeys():
            data = self.data.GetImageData( data_name )
            actor_tp = vtk_actor.vtkImageActorPipe
        elif data_name in self.data.GetPolyDataKeys():
            data = self.data.GetPolyData( data_name )
            actor_tp = vtk_actor.vtkGraphActorPipe
        if data is not None:
            self.active_actor = self.active_renwin.FromActor( data_name, data, actor_tp )
            self.Render()
        
        
    def DelActor( self, data_name ):
        self.active_renwin.DelActor( data_name )
        self.data.DeleteData( data_name )
        self.Render()
    
    
    def active( self ):
        return self.active_actor is not None
    
    def SetCurrentActor( self, data_name ):
        self.active_actor = self.active_renwin.GetActor( data_name )
        if self.active():
            vis, clr, opac, thresh, fore = self.active_actor.GetParams()
            self.fillWidg( vis, clr, opac, thresh, fore )
            
    
    def SetStPt( self, pt, rad=1 ):
        self.slots[0].window.SetStPt( pt, rad )
            
            
    def SetColor( self, r,g,b ):
        if self.active_actor is not None:
            self.active_actor.SetColor( r,g,b )
            self.Render()
            
    def SetOpacity( self, val ):
        if self.active_actor is not None:
            self.active_actor.SetOpacity( val )
            self.Render()
            
    def SetVisibility( self, bl ):
        if self.active_actor is not None:
            self.active_actor.SetVisibility( bl )
            self.Render()
            
    def SetForeground( self, bl ):
        if self.active_actor is not None:
            self.slots[0].window.ToForeground( self.active_actor, bl )
            self.Render()
            
    def SetActorParams( self, data_name, clr, opac, vis=True ):
        self.SetCurrentActor( data_name )
        self.SetColor( clr[0], clr[1], clr[2] )
        self.SetOpacity( opac )
        self.SetVisibility( vis )
        
        
    def SetThreshold( self, thresh ):
        if self.active_actor is not None:
            try: self.active_actor.SetThreshold( thresh )
            except: self.active_actor.SetLineWidth( thresh )
            self.Render()
            
            
    def Clear( self ):
        self.data.Clear()
        for slot in self.slots:
            slot.Clear()
        
        
    def Update( self ):
        for slot in self.slots:
            slot.Update()
        self.Render()

    
    
    def Initialize( self ):
        self.win_inter.Initialize()
        self.GetRenderWindow().Render() 
        
