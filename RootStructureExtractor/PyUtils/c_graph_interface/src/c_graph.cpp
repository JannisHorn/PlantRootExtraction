/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "c_graph.h"
#include "c_graph_node.h"

extern "C"
{

void CGraph_dealloc( CGraph* self )
{
  if( self->is_owner )
  {
    self->graph_ptr->clear();
    free( self->graph_ptr );
  }
  Py_TYPE( self )->tp_free( (PyObject*)self );
}


PyObject* CGraph_new( PyTypeObject* type, PyObject* args, PyObject* kwds )
{
  CGraph* self;
  self = ( CGraph* )type->tp_alloc( type, 0 );

  self->graph_ptr = nullptr;
  self->iter = -1;

  return (PyObject*) self;
}


int CGraph_init( CGraph* self, PyObject* args, PyObject* kwds )
{
  static char *kwlist[] = { "graph_ptr", nullptr };

  long graph_ptr;
  if( !PyArg_ParseTupleAndKeywords( args, kwds, "l", kwlist, &(graph_ptr) ) )
    return -1;

  if( graph_ptr != 0 )
    self->graph_ptr = reinterpret_cast<utils::RootGraph*>( graph_ptr );
  else
  {
    utils::RootGraph::Node* root = new utils::RootGraph::Node();
    self->graph_ptr = new utils::RootGraph( root );
  }

  return 0;
}

PyObject* CGraph_getPointer( CGraph* self )
{
  PyObject* graph_ptr = PyLong_FromLong( reinterpret_cast<intptr_t>( self->graph_ptr ) );
  Py_INCREF( graph_ptr );
  return graph_ptr;
}


PyObject* CGraph_getRoot( CGraph* self )
{
  //PyObject* py_root = CGraphNode_newFromGraph( self->graph_ptr->getRoot() );
  //std::cout << "Rad " << PyLong_AsLong( CGraphNode_getRad( ((CGraphNode*)py_root) ) ) << std::endl;

  return graphNodeToPyInt( self->graph_ptr->getRoot() );
}


PyObject* CGraph_setRoot( CGraph* self, PyObject* args )
{
  PyObject* c_node;
  if( !PyArg_ParseTuple( args, "O", &c_node ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraph_setRoot: Wrong number of arguments." );
    return NULL;
  }

  utils::RootGraph::Node* old_root = self->graph_ptr->getRoot();
  utils::RootGraph::Node* new_root = ((CGraphNode*)c_node)->node_ptr;
  old_root->getVal() = new_root->getVal();
  old_root->disconnect();

  for( int c_it=0; c_it < new_root->rank() ; ++c_it )
    old_root->insert( new_root->getChild( c_it ) );
  new_root->disconnect();
  free( new_root );

  Py_INCREF( Py_None );
  return Py_None;
}


void CGraph_clear( CGraph* self )
{
  self->graph_ptr->clear();
}


PyObject* CGraph_size( CGraph* self )
{
  PyObject* size = PyLong_FromSize_t( self->graph_ptr->size() );
  Py_INCREF( size );
  return size;
}


PyObject* CGraph_rotate( CGraph* self, PyObject* args )
{
  double a, b, c;
  if( !PyArg_ParseTuple( args, "ddd", &a, &b, &c ) )
    return NULL;

  self->graph_ptr->rotate( a, b, c );
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_translate( CGraph* self, PyObject* args )
{
  double x, y, z;
  if( !PyArg_ParseTuple( args, "ddd", &x, &y, &z ) )
    return NULL;

  self->graph_ptr->translate( utils::CoordinateD(x,y,z) );
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_zeroRoot( CGraph* self )
{
  self->graph_ptr->zeroRoot();
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_evaluateRootID( CGraph* self )
{
  self->graph_ptr->evaluateRootID();
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_repairRadius( CGraph* self )
{
  self->graph_ptr->repairRadius();
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_repairPreds( CGraph* self )
{
  self->graph_ptr->repairPreds();
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_repairTips( CGraph* self )
{
  self->graph_ptr->repairRootTips();
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraph_toVolume( CGraph* self, PyObject* args )
{
  PyObject* py_coor;
  if( !PyArg_ParseTuple( args, "O", &py_coor ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraph_toVolume: Wrong number of arguments." );
    return NULL;
  }

  int ls_length = PyObject_Length( py_coor );
  if( ls_length < 3 )
  {
    PyErr_SetString( PyExc_TypeError, "CGraph_toVolume: Wrong number of list coords." );
    return NULL;
  }

  int x_max = PyLong_AsLong( PyList_GetItem( py_coor, 0 ) );
  int y_max = PyLong_AsLong( PyList_GetItem( py_coor, 1 ) );
  int z_max = PyLong_AsLong( PyList_GetItem( py_coor, 2 ) );

  Volume out( z_max, y_max, x_max ); //Volume inverses x and z dimensions!
  self->graph_ptr->draw( out );

  return volumeToNumpy( out );
}


PyObject* CGraph_getDensePoints( CGraph* self, PyObject* args )
{
  double mdist;
  if( !PyArg_ParseTuple( args, "d", &mdist ) )
    return NULL;

  std::vector<std::vector<utils::CoordinateD>> pt_list;
  self->graph_ptr->getDensePointList( pt_list, mdist );

  size_t len = 0;
  for( const std::vector<utils::CoordinateD>& pt_vec : pt_list )
    len += pt_vec.size();
  PyObject* py_list_out;
  py_list_out = PyList_New( len );

  size_t l_it = 0;
  for( const std::vector<utils::CoordinateD>& pt_vec : pt_list )
    for( const utils::CoordinateD& pt : pt_vec )
    {
      PyObject* py_pt = PyList_New( 3 );
      PyList_SET_ITEM( py_pt, 0, PyFloat_FromDouble( pt[0] ) );
      PyList_SET_ITEM( py_pt, 1, PyFloat_FromDouble( pt[1] ) );
      PyList_SET_ITEM( py_pt, 2, PyFloat_FromDouble( pt[2] ) );
      PyList_SET_ITEM( py_list_out, l_it, py_pt );
      ++l_it;
    }

  Py_INCREF( py_list_out );
  return py_list_out;
}


PyObject* CGraph_toStr( CGraph* self )
{
  PyObject* out = PyUnicode_FromString( self->graph_ptr->toXml().c_str() );
  Py_INCREF( out );
  return out;
}


PyObject* CGraph_setOwnership( CGraph* self, PyObject* args )
{
  bool own;
  if( !PyArg_ParseTuple( args, "p", &own ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraph_setOwnership: Wrong number of arguments." );
    return NULL;
  }

  self->is_owner = own;
  Py_INCREF( Py_None );
  return Py_None;
}

}
