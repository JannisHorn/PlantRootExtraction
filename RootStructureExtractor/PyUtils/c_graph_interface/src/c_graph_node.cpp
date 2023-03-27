/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "c_graph_node.h"

extern "C"
{

void CGraphNode_dealloc( CGraphNode* self )
{
  //if( self->is_owner )
  //  free( self->node_ptr );
  Py_TYPE( self )->tp_free( (PyObject*)self );
}


PyObject* CGraphNode_new( PyTypeObject* type, PyObject* args, PyObject* kwds )
{
  CGraphNode* self;
  self = ( CGraphNode* )type->tp_alloc( type, 0 );

  self->node_ptr = nullptr;

  return (PyObject*) self;
}


int CGraphNode_init( CGraphNode* self, PyObject* args, PyObject* kwds )
{
  static char *kwlist[] = { "node_ptr", nullptr };
  long temp_ptr;

  if( !PyArg_ParseTupleAndKeywords( args, kwds, "l", kwlist, &temp_ptr ) )
    return -1;

  if( temp_ptr == 0 )
    self->node_ptr = new utils::RootGraph::Node();
  else
    self->node_ptr = reinterpret_cast<utils::RootGraph::Node*>( temp_ptr );

  return 0;
}


PyObject* CGraphNode_newFromGraph( utils::RootGraph::NodePtr from_node )
{
  PyObject* py_node;
  py_node = (PyObject*)PyObject_New( CGraphNode, &PyCGraphNodeType );
  py_node = PyObject_Init( (PyObject*)py_node, &PyCGraphNodeType );

  //PyObject *arg_list = Py_BuildValue( "i", from_node );
  //std::cout << "Call" << std::endl;
  //PyObject *py_node = PyObject_CallObject((PyObject *) &PyCGraphNodeType, arg_list);
  Py_INCREF( py_node );

  if( py_node == nullptr )
    std::cout << "Bad Init" << std::endl;

  //Py_DECREF( arg_list );
  ((CGraphNode*)py_node)->node_ptr = from_node;

  return (PyObject*)py_node;
}


PyObject* CGraphNode_getPtr( CGraphNode* self )
{
  return graphNodeToPyInt( self->node_ptr );
}


PyObject* CGraphNode_setPtr( CGraphNode* self, PyObject* args )
{
  long temp_ptr;
  if( !PyArg_ParseTuple( args, "l", &temp_ptr ) )
    return NULL;

  self->node_ptr = reinterpret_cast<utils::RootGraph::Node*>( temp_ptr );

  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraphNode_getBranchId( CGraphNode* self )
{
  PyObject* py_id = PyLong_FromSize_t( self->node_ptr->getVal().branch_id );
  Py_INCREF( py_id );
  return py_id;
}


PyObject* CGraphNode_setBranchId( CGraphNode* self, PyObject* args )
{
  size_t n_id;
  if( !PyArg_ParseTuple( args, "l", &n_id ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_setBranchId: Wrong number of arguments." );
    return NULL;
  }

  self->node_ptr->getVal().branch_id = n_id;
  Py_INCREF( Py_None );
  return Py_None;
}



PyObject* CGraphNode_getCoor( CGraphNode* self )
{
  utils::Coordinate& coor = self->node_ptr->getVal().pos;

  PyObject* py_coor;
  py_coor = PyList_New( 3 );

  PyList_SetItem( py_coor, 0, PyLong_FromLong( int64_t( coor.x() ) ) );
  PyList_SetItem( py_coor, 1, PyLong_FromLong( int64_t( coor.y() ) ) );
  PyList_SetItem( py_coor, 2, PyLong_FromLong( int64_t( coor.z() ) ) );

  Py_INCREF( py_coor );
  return py_coor;
}


PyObject* CGraphNode_setCoor( CGraphNode* self, PyObject* args )
{
  PyObject* py_coor;
  if( !PyArg_ParseTuple( args, "O", &py_coor ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_setCoor: Wrong number of arguments." );
    return NULL;
  }

  int ls_length = PyObject_Length( py_coor );
  if( ls_length < 3 )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_setCoor: Wrong number of list coords." );
    return NULL;
  }

  int x = PyLong_AsLong( PyList_GetItem( py_coor, 0 ) );
  int y = PyLong_AsLong( PyList_GetItem( py_coor, 1 ) );
  int z = PyLong_AsLong( PyList_GetItem( py_coor, 2 ) );
  utils::Coordinate coor( x, y, z );

  self->node_ptr->getVal().pos = coor;
  Py_INCREF( Py_None );
  return Py_None;
}



PyObject* CGraphNode_getRad( CGraphNode* self )
{
  PyObject* py_rad = PyFloat_FromDouble( double( self->node_ptr->getVal().rad ) );
  Py_INCREF( py_rad );
  return py_rad;
}


PyObject* CGraphNode_setRad( CGraphNode* self, PyObject* args )
{
  double n_rad;
  if( !PyArg_ParseTuple( args, "d", &n_rad ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_setRad: Wrong number of arguments." );
    return NULL;
  }

  self->node_ptr->getVal().rad = n_rad;
  Py_INCREF( Py_None );
  return Py_None;
}



PyObject* CGraphNode_getChildren( CGraphNode* self )
{
  PyObject* py_child_list;
  const utils::RootGraph::NodeVector& child_vec = ((CGraphNode*)self)->node_ptr->getChilds();

  py_child_list = PyList_New( child_vec.size() );
  for( size_t c_it=0; c_it < child_vec.size() ; ++c_it )
    PyList_SetItem( py_child_list, c_it, graphNodeToPyInt( child_vec[c_it] ) );

  Py_INCREF( py_child_list );
  return py_child_list;
}


PyObject* CGraphNode_getChild( CGraphNode* self, PyObject* args )
{
  long it;
  if( !PyArg_ParseTuple( args, "l", &it ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_getChild: Wrong number of arguments." );
    return NULL;
  }

  if( it < self->node_ptr->rank() )
    return graphNodeToPyInt( self->node_ptr->getChild( it ) );
  else
  {
    PyErr_SetString( PyExc_IndexError, "CGraphNode_getChild: Iterator out of range." );
    return NULL;
  }
}


PyObject* graphNodeToPyInt( utils::RootGraph::NodePtr from_node )
{
  PyObject* node_ptr = PyLong_FromLong( reinterpret_cast<intptr_t>( from_node ) );
  Py_INCREF( node_ptr );
  return node_ptr;
}


PyObject* CGraphNode_append( CGraphNode* self, PyObject* args )
{
  PyObject* c_node;
  if( !PyArg_ParseTuple( args, "O", &c_node ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_append: Wrong number of arguments." );
    return NULL;
  }

  self->node_ptr->insert( ((CGraphNode*)c_node)->node_ptr );
  Py_INCREF( Py_None );
  return Py_None;
}


PyObject* CGraphNode_rank( CGraphNode* self )
{
  PyObject* rank = PyLong_FromSize_t( self->node_ptr->rank() );
  Py_INCREF( rank );
  return rank;
}

PyObject* CGraphNode_getItem( PyObject* self, Py_ssize_t it )
{
  if( it < ((CGraphNode*)self)->node_ptr->rank() )
    return graphNodeToPyInt( ((CGraphNode*)self)->node_ptr->getChild( it ) );
  else
  {
    PyErr_SetString( PyExc_IndexError, "CGraphNode_getChild: Iterator out of range." );
    return NULL;
  }
}


Py_ssize_t CGraphNode_length( CGraphNode* self )
{
  return Py_ssize_t( self->node_ptr->rank() );
}


PyObject* CGraphNode_setOwnership( CGraphNode* self, PyObject* args )
{
  bool own;
  if( !PyArg_ParseTuple( args, "p", &own ) )
  {
    PyErr_SetString( PyExc_TypeError, "CGraphNode_setOwnership: Wrong number of arguments." );
    return NULL;
  }

  //self->is_owner = own;
  Py_INCREF( Py_None );
  return Py_None;
}

}
