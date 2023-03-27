/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef C_GRAPH_H__
#define C_GRAPH_H__

extern "C" {
  #include <Python.h>
  #include "structmember.h"
}
#include "root_graph.h"
#include "volume.h"
#include "volume_to_npy.h"

extern "C"
{

typedef struct
{
  PyObject_HEAD
  utils::RootGraph *graph_ptr;
  size_t iter;
  bool is_owner;
} CGraph;


void CGraph_dealloc( CGraph* self );

PyObject* CGraph_new( PyTypeObject* type, PyObject* args, PyObject* kwds );

int CGraph_init( CGraph* self, PyObject* args, PyObject* kwds );

PyObject* CGraph_getPointer( CGraph* self );

PyObject* CGraph_getRoot( CGraph* self );
PyObject* CGraph_setRoot( CGraph* self, PyObject* args );

void CGraph_clear( CGraph* self );
PyObject* CGraph_size( CGraph* self );

PyObject* CGraph_rotate( CGraph* self, PyObject* args );
PyObject* CGraph_translate( CGraph* self, PyObject* args );
PyObject* CGraph_zeroRoot( CGraph* self );

PyObject* CGraph_evaluateRootID( CGraph* self );
PyObject* CGraph_repairRadius( CGraph* self );
PyObject* CGraph_repairPreds( CGraph* self );
PyObject* CGraph_repairTips( CGraph* self );

PyObject* CGraph_toVolume( CGraph* self, PyObject* args );
PyObject* CGraph_getDensePoints( CGraph* self, PyObject* args );

PyObject* CGraph_toStr( CGraph* self );
PyObject* CGraph_setOwnership( CGraph* self, PyObject* args );

static PyMethodDef CGraph_methods[] = {
  { "getPointer", (PyCFunction)CGraph_getPointer, METH_NOARGS,
    "Get C Graph Pointer" },
  { "getRoot", (PyCFunction)CGraph_getRoot, METH_NOARGS,
    "Get python wrapper of root node"},
  { "setRoot", (PyCFunction)CGraph_setRoot, METH_VARARGS,
    "Set root node from cnode ptr" },
  { "clear", (PyCFunction)CGraph_clear, METH_NOARGS,
    "Clear the complete underlying CGraph" },
  { "size", (PyCFunction)CGraph_size, METH_NOARGS,
    "Get number of graph nodes" },
  { "rotate", (PyCFunction)CGraph_rotate, METH_VARARGS,
    "Rotate Graph around (0,0,0), Args in degree" },
  { "translate", (PyCFunction)CGraph_translate, METH_VARARGS,
    "Translate Graph" },
  { "zeroRoot", (PyCFunction)CGraph_zeroRoot, METH_NOARGS,
    "Translate Graph to have Root as Zero" },
  { "evaluateRootID", (PyCFunction)CGraph_evaluateRootID, METH_NOARGS,
    "Reevaluate root ids" },
  { "repairRadius", (PyCFunction)CGraph_repairRadius, METH_NOARGS,
    "Repair radius=1 segments by linear interpolation" },
  { "repairPreds", (PyCFunction)CGraph_repairPreds, METH_NOARGS,
    "Reset predecessor node for all graph nodes." },
  { "repairTips", (PyCFunction)CGraph_repairTips, METH_NOARGS,
    "Reset root tip radius to be larger 0.0." },
  { "toVolume", (PyCFunction)CGraph_toVolume, METH_VARARGS,
    "Creates numpy array from volume" },
  { "getDensePointList", (PyCFunction)CGraph_getDensePoints, METH_VARARGS,
    "Create dense point list from CGraph" },
  { "toStr", (PyCFunction)CGraph_toStr, METH_VARARGS,
    "Get Raw xml string" },
  { "setOwnership", (PyCFunction)CGraph_setOwnership, METH_VARARGS,
    "Set underlying Ownership for data deallocation on object end." },
  { nullptr }
};

static PyTypeObject PyCGraphType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "c_graph.CGraph",             /* tp_name */
    sizeof(CGraph),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)CGraph_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "Interface to extract information from C Graph Nodes",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    CGraph_methods,             /* tp_methods */
    0,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CGraph_init,      /* tp_init */
    0,                         /* tp_alloc */
    (newfunc)CGraph_new,       /* tp_new */
};

}

#endif // C_GRAPH_H__
