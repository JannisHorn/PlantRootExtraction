#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from PyQt5.QtCore import QObject, pyqtSignal
import threading
import _thread
import ctypes

class Algorithm( threading.Thread ):
    def __init__( self ):
        super().__init__()
        
    def setFunction( self, func, *args ):
        self.func = func
        self.args = args
        
    def run( self ):
        try:
            self.startedCallback()
            if len( self.args ) == 0: self.func()
            else: self.func( self.args ) 
        except IOError as e:
            raise e
        finally:
            self.finishedCallback()
            print( "Thread killed" )
    
    def raiseException( self ):
        #_thread.exit()
        thread_id = threading.get_ident()
        #res = ctypes.pythonapi.PyThreadState_SetAsyncExc( thread_id, ctypes.py_object(SystemExit) )
        #if res > 1: 
        ctypes.pythonapi.PyThreadState_SetAsyncExc( thread_id, ctypes.py_object(IOError) )
        print( "{0}: Exception called".format( thread_id ) )
    
    def setStartedCallback( self, func ):
        self.startedCallback = func
            
    def setFinishedCallback( self, func ):
        self.finishedCallback = func


class AlgorithmController( QObject ):
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal( IOError )
    def __init__( self ):
        super().__init__()
        
    def initThread( self ):
        self.algo = Algorithm()
        self.algo.daemon = True
        self.algo.setFinishedCallback( self.finishedCallback )
        self.algo.setStartedCallback( self.startedCallback )
        
    def setFunction( self, func, *args ):
        self.initThread()
        self.algo.setFunction( func, *args )
        
    def startedCallback( self ):
        self.started.emit()
        
    def finishedCallback( self ):
        self.finished.emit()
        
    def start( self ):
        self.algo.start()
        
    def stop( self ):
        self.algo.raiseException()
        self.algo.join()
