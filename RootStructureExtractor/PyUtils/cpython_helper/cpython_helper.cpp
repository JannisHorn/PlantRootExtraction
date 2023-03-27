extern "C" {
  #include <Python.h>
  #include "structmember.h"
}
#include <vector>
#include "utils.h"

extern "C"
{

PyObject* cpython_helper_vectorToList( const std::vector<utils::Coordinate>& pos_vec )
{
  PyObject* py_pos_list;
  py_pos_list = PyList_New( child_vec.size() );

  for( size_t v_it=0; v_it < pos_vec.size(); ++v_it )
  {
    PyObject* py_pos;
    py_pos = PyList_New( 3 );
    PyList_SetItem( py_child_list, v_it, graphNodeToPyInt( child_vec[c_it] ) );


  }
  Py_INCREF( py_child_list );
  return py_child_list;
}

}
