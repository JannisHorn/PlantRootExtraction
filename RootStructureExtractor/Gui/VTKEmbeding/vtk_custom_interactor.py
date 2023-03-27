#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import vtk

class vtkInteractorStyleController( vtk.vtkCallbackCommand ):
    
    def __init__( self, parent=None ):
        super().__init__()
        self.parent = parent
        self.cur_renderer = vtk.vtkRenderer()
        
        
    def GetPokedRenderer( self ):
        mouse_pos = self.parent.GetEventPosition()
        return self.parent.FindPokedRenderer( mouse_pos[0], mouse_pos[1] )
    
    
    def SetInteractorStyle( self, renderer ):
        self.parent.SetInteractorStyle( renderer.GetInteractorStyle() )
        
        
    def GetInteractorStyle( self ):
        return self.parent.GetInteractorStyle()
        
    
    def __call__( self, caller, event ):
        renderer = self.GetPokedRenderer()
        if not renderer == self.cur_renderer:
            self.cur_renderer = renderer
            self.GetInteractorStyle().OnLeftButtonUp()
            self.SetInteractorStyle( self.cur_renderer )
        else:
            self.GetInteractorStyle().OnMouseMove()
            
    
    

class vtkInteractorStyleImageSlice( vtk.vtkInteractorStyleImage ):
    
    def __init__( self, picker, parent=None ):
        super().__init__()
        self.parent = parent
        self.picker = picker
        self.AddObserver("KeyPressEvent",self.OnKeyDown)
        self.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        
        
    def SetRenderer( self, renderer ):
        self.renderer = renderer
        
        
    def OnLeftButtonDown( self, obj, event ):
        event_pos = self.parent.GetEventPosition()
        status = self.picker.Pick( event_pos[0], event_pos[1], 0, self.renderer )
        if status > 0:
            self.renderer.SetPoint( self.picker.GetPickPosition() )
        else:
            self.renderer.SetPoint( None )
        
        
    def OnKeyDown( self, obj, event ):
        key = self.parent.GetKeySym()
        if key == "Right":
            self.renderer.IncrementSlice()
        elif key == "Left":
            self.renderer.DecrementSlice()
        elif key == 'r':
            self.renderer.ResetCamera()
            


class vtkInteractorTrackballPicker( vtk.vtkInteractorStyleTrackballCamera ):
    
    def __init__( self, picker, parent=None ):
        super().__init__()
        self.picker = picker
        self.parent = parent
        self.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)


    def SetRenderer( self, renderer ):
        self.renderer = renderer


    def OnLeftButtonDown( self, obj, event ):
        event_pos = self.parent.GetEventPosition()
        status = self.picker.Pick( event_pos[0], event_pos[1], 0, self.renderer )
        if status > 0:
            self.renderer.SetPoint( self.picker.GetPickPosition() )
        else:
            self.renderer.SetPoint( None )
        super().OnLeftButtonDown()
        
        
