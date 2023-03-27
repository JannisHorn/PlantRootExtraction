/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef VOLUME_TO_NUMPY_H__
#define VOLUME_TO_NUMPY_H__

extern "C"{
  #include "Python.h"
  #include "numpy/arrayobject.h"
}
#include "volume.h"
#include <exception>
#include <type_traits>

template<class _Tp>
inline long templateToTypenum()
{
  if( std::is_same<int, _Tp>::value ) return NPY_INT32;
  if( std::is_same<long, _Tp>::value ) return NPY_INT64;
  if( std::is_same<size_t, _Tp>::value ) return NPY_UINT64;
  if( std::is_same<float, _Tp>::value ) return NPY_FLOAT32;
  if( std::is_same<double, _Tp>::value ) return NPY_FLOAT64;
  return -1;
}


template<class _Tp>
inline PyObject* volumeToNumpy( VolumeBase<_Tp>& inp )
{
  import_array();
  inp.setOwner( false );
  int dt_tp = templateToTypenum<_Tp>();
  if( dt_tp == -1 ) throw std::runtime_error( std::string( __func__ ) +std::string( ": invalid datatype! Could not convert." ) );

  long arr_size[3];
  arr_size[0] = inp.getShape()[2];
  arr_size[1] = inp.getShape()[1];
  arr_size[2] = inp.getShape()[0];

  PyObject* out = PyArray_SimpleNewFromData( 3, &arr_size[0], dt_tp, inp.getData() );
  Py_INCREF( out );

  return out;
}

#endif // VOLUME_TO_NUMPY_H__

