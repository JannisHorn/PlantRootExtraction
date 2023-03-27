/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef C_GRAPH_NODE__
#define C_GRAPH_NODE__

extern "C" {
  #include <Python.h>
  #include "structmember.h"
}
#include "root_graph.h"

extern "C"
{

typedef struct
{
  PyObject_HEAD
  utils::RootGraph::NodePtr node_ptr;
} CGraphNode;

void CGraphNode_dealloc( CGraphNode* self );

PyObject* CGraphNode_new( PyTypeObject* type, PyObject* args, PyObject* kwds );

int CGraphNode_init( CGraphNode* self, PyObject* args, PyObject* kwds );

PyObject* CGraphNode_newFromGraph( utils::RootGraph::NodePtr from_node );


PyObject* CGraphNode_setPtr( CGraphNode* self, PyObject* args );
PyObject* CGraphNode_getPtr( CGraphNode* self );

PyObject* CGraphNode_getBranchId( CGraphNode* self );
PyObject* CGraphNode_setBranchId( CGraphNode* self, PyObject* args );

PyObject* CGraphNode_getCoor( CGraphNode* self );
PyObject* CGraphNode_setCoor( CGraphNode* self, PyObject* args );

PyObject* CGraphNode_getRad( CGraphNode* self );
PyObject* CGraphNode_setRad( CGraphNode* self, PyObject* args );

PyObject* CGraphNode_getChildren( CGraphNode* self );
PyObject* CGraphNode_getChild( CGraphNode* self, PyObject* args );
PyObject* CGraphNode_append( CGraphNode* self, PyObject* args );
PyObject* CGraphNode_rank( CGraphNode* self );
PyObject* CGraphNode_getItem( PyObject* self, Py_ssize_t it );
Py_ssize_t CGraphNode_length( CGraphNode* self );

PyObject* CGraphNode_setOwnership( CGraphNode* self, PyObject* args );

PyObject* graphNodeToPyInt( utils::RootGraph::NodePtr from_node );


static PyMethodDef CGraphNode_methods[] = {
  { "setPtr", (PyCFunction)CGraphNode_setPtr, METH_VARARGS,
    "Set raw c_ptr" },
  { "getPtr", (PyCFunction)CGraphNode_getPtr, METH_NOARGS,
    "Get raw c_ptr" },
  { "getBranchId", (PyCFunction)CGraphNode_getBranchId, METH_NOARGS,
    "Get Branch Id of Graph Node"},
  { "setBranchId", (PyCFunction)CGraphNode_setBranchId, METH_VARARGS,
    "Set Node BranchId from Integer" },
  { "getCoor", (PyCFunction)CGraphNode_getCoor, METH_NOARGS,
    "Get 3D Coordinates of Graph Node" },
  { "setCoor", (PyCFunction)CGraphNode_setCoor, METH_VARARGS,
    "Set Node Coordinate from List" },
  { "getRad", (PyCFunction)CGraphNode_getRad, METH_NOARGS,
    "Get Radius in voxel units" },
  { "setRad", (PyCFunction)CGraphNode_setRad, METH_VARARGS,
    "Set Node Radius from double" },
  { "getChildren", (PyCFunction)CGraphNode_getChildren, METH_NOARGS,
    "Get PyList with CGraphNode objects of child nodes" },
  { "getChild", (PyCFunction)CGraphNode_getChild, METH_VARARGS,
    "Get child by iterator" },
  { "append", (PyCFunction)CGraphNode_append, METH_VARARGS,
    "Add input Node after this node" },
  { "rank", (PyCFunction)CGraphNode_rank, METH_NOARGS,
    "Get number of children" },
  { "setOwnership", (PyCFunction)CGraphNode_setOwnership, METH_VARARGS,
    "Couple Ownership with PyWrapper" },
  { nullptr }
};

static PySequenceMethods PyCGraphNodeSequence = {
    .sq_length = (lenfunc)CGraphNode_length,
    .sq_item = CGraphNode_getItem
};

static PyTypeObject PyCGraphNodeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "c_graph.CGraphNode",
    .tp_basicsize = sizeof( CGraphNode ),
    .tp_dealloc = (destructor)CGraphNode_dealloc,
    .tp_as_sequence = &PyCGraphNodeSequence,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "Interface to extract information from C Graph Nodes",
    .tp_methods = CGraphNode_methods,
    .tp_init = (initproc)CGraphNode_init,
    .tp_new = (newfunc)CGraphNode_new,
};


//static PyTypeObject PyCGraphNodeType = {
//    PyVarObject_HEAD_INIT(NULL, 0)
//    "c_graph.CGraphNode",             /* tp_name */
//    sizeof(CGraphNode),             /* tp_basicsize */
//    0,                         /* tp_itemsize */
//    (destructor)CGraphNode_dealloc, /* tp_dealloc */
//    0,                         /* tp_print */
//    0,                         /* tp_getattr */
//    0,                         /* tp_setattr */
//    0,                         /* tp_reserved */
//    0,                         /* tp_repr */
//    0,                         /* tp_as_number */
//    0,                         /* tp_as_sequence */
//    0,                         /* tp_as_mapping */
//    0,                         /* tp_hash  */
//    0,                         /* tp_call */
//    0,                         /* tp_str */
//    0,                         /* tp_getattro */
//    0,                         /* tp_setattro */
//    0,                         /* tp_as_buffer */
//    Py_TPFLAGS_DEFAULT |
//        Py_TPFLAGS_BASETYPE,   /* tp_flags */
//    "Interface to extract information from C Graph Nodes",           /* tp_doc */
//    0,                         /* tp_traverse */
//    0,                         /* tp_clear */
//    0,                         /* tp_richcompare */
//    0,                         /* tp_weaklistoffset */
//    0,                         /* tp_iter */
//    0,                         /* tp_iternext */
//    CGraphNode_methods,             /* tp_methods */
//    0,             /* tp_members */
//    0,                         /* tp_getset */
//    0,                         /* tp_base */
//    0,                         /* tp_dict */
//    0,                         /* tp_descr_get */
//    0,                         /* tp_descr_set */
//    0,                         /* tp_dictoffset */
//    (initproc)CGraphNode_init,      /* tp_init */
//    0,                         /* tp_alloc */
//    (newfunc)CGraphNode_new,        /* tp_new */
//};

}

#endif // C_GRAPH_NODE__
