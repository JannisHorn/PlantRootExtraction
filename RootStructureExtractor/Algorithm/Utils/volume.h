/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */


#ifndef VOLUME_H__
#define VOLUME_H__

#include <vector>
#include <cstring>
#include <sstream>
#include <mutex>
#include <memory>
#include "utils.h"


template <class _Tp>
class ArrayController
{
public:
  ArrayController( const size_t array_size ){ m_data = (_Tp*) malloc( array_size *sizeof( _Tp ) ); }
  ArrayController( void* data ):m_is_owner(false){ m_data = reinterpret_cast<_Tp*>( data ); }
  ArrayController( _Tp* data ):m_is_owner(false){ m_data = reinterpret_cast<_Tp*>( data ); }
  ~ArrayController() { if( m_is_owner ) free( m_data ); }
  inline void setOwner( const bool& is_owner ) { m_is_owner = is_owner; }
  inline _Tp& operator[]( const size_t it ){ return m_data[it]; }
  inline const _Tp& operator[]( const size_t it ) const { return m_data[it]; }
  inline _Tp* data(){ return m_data; }
  inline void lockArray() { m_is_owner = false; }
  inline void copyFrom( const _Tp* other, const size_t& size, const bool& relock=true )
  {
    if( relock && m_is_owner ) m_data = (_Tp*)realloc( m_data, size *sizeof(_Tp) );
    memcpy( m_data, other, size );
  }
private:
  _Tp* m_data;
  bool m_is_owner = true;
};

template <class _Tp>
class VolumeBase
{
public:
  VolumeBase() : m_shape( utils::Coordinate(0,0,0) ), m_z_step( 0 ), m_size( 0 ) {};
  VolumeBase( const size_t x_dim, const size_t y_dim, const size_t z_dim )
  {
    m_shape = utils::Coordinate( x_dim, y_dim, z_dim );
    m_z_step = x_dim *y_dim;
    m_size = x_dim *y_dim *z_dim;
    m_data = std::make_shared<ArrayController<_Tp>>( m_size );
    fill( 0 );
  }
  VolumeBase( const utils::Coordinate& coord )
  {
    m_shape = utils::Coordinate( coord[0], coord[1], coord[2] );
    m_z_step = coord[0] *coord[1];
    m_size = coord[0] *coord[1] *coord[2];
    m_data = std::make_shared<ArrayController<_Tp>>( m_size );
    fill( 0 );
  }
  VolumeBase( const utils::Coordinate& coord, const _Tp& filler )
  {
    m_shape = utils::Coordinate( coord[0], coord[1], coord[2] );
    m_z_step = coord[0] *coord[1];
    m_size = coord[0] *coord[1] *coord[2];
    m_data = std::make_shared<ArrayController<_Tp>>( m_size );
    fill( filler );
  }
  VolumeBase( void* data, const utils::Coordinate& shape )
  {
    m_shape = shape;
    m_z_step = shape[0] *shape[1];
    m_size = shape[0] *shape[1] *shape[2];
    m_data = std::make_shared<ArrayController<_Tp>>( data );
  }
  VolumeBase( _Tp* data, const utils::Coordinate& shape )
  {
    m_shape = shape;
    m_z_step = shape[0] *shape[1];
    m_size = shape[0] *shape[1] *shape[2];
    m_data = std::make_shared<ArrayController<_Tp>>( data );
  }
  VolumeBase( const VolumeBase<_Tp>& other )
  {
    m_shape = other.getShape();
    m_z_step = m_shape[0] *m_shape[1];
    m_size = m_shape[0] *m_shape[1] *m_shape[2];
    m_data = std::make_shared<ArrayController<_Tp>>( m_size );
    m_data->copyFrom( other.getData(), m_size, false );
  }
  VolumeBase( VolumeBase<_Tp>&& vl )
  {
    m_shape = std::move( vl.m_shape );
    m_z_step = std::move( vl.m_z_step );
    m_size = std::move( vl.m_size );
    m_data = std::move( vl.m_data );
  }
  ~VolumeBase(){}

  inline VolumeBase<_Tp>& operator=( VolumeBase<_Tp>& input ) { return input; }
  inline VolumeBase<_Tp>& operator=( VolumeBase<_Tp>&& input )
  {
    m_data = std::move( input.m_data );
    m_size = std::move( input.m_size );
    m_shape = std::move( input.m_shape );
    m_z_step = std::move( input.m_z_step );
    return *this;
  }
  inline _Tp& operator()( const size_t x, const size_t y, const size_t z ) { return getData( getIndex( x,y,z ) ); }
  inline const _Tp& operator()( const size_t x, const size_t y, const size_t z ) const { return getData( getIndex( x,y,z ) ); }
  inline _Tp& operator()( const int x, const int y, const int z ) { return getData( getIndex( x,y,z ) ); }
  inline const _Tp& operator()( const int x, const int y, const int z ) const { return getData( getIndex( x,y,z ) ); }
  inline _Tp& operator()( const utils::Coordinate coord ) { return operator()( coord[0], coord[1], coord[2] ); }
  inline const _Tp& operator()( const utils::Coordinate coord ) const { return operator()( coord[0], coord[1], coord[2] ); }
  inline _Tp& operator[]( const size_t it ) { return getData(it); }
  inline const _Tp& operator[]( const size_t it ) const { return getData(it); }

  inline const utils::Coordinate& getShape() const { return m_shape; }
  inline size_t getSize() const { return m_size; }
  inline _Tp* getData() { return m_data->data(); }
  inline const _Tp* getData() const { return m_data->data(); }
  inline _Tp& getData( const size_t it ){ return (*m_data)[it]; }
  inline const _Tp& getData( const size_t it ) const { return (*m_data)[it]; }
  inline void setData( const size_t x, const size_t y, const size_t z, const _Tp val ) { memcpy( &getData(getIndex(x,y,z)), &val, sizeof(_Tp) ); }
  inline ArrayController<_Tp>* getDataPtr() const { return m_data.get(); }
  inline void setOwner( const bool& is_owner ) { m_data->setOwner( is_owner ); }

  inline void copyFrom( const VolumeBase<_Tp>& other )
  {
    m_shape = other.getShape();
    m_z_step = m_shape[0] *m_shape[1];
    const bool relock = m_size != other.getSize();
    m_size = m_z_step *m_shape[2];
    m_data->copyFrom( other.getData(), m_size, relock );
  }

  inline void fill( const _Tp val )
  {
    std::fill( &getData(0), &getData(m_size), val );
  }

  inline _Tp sum() const
  {
    _Tp run_sum = 0;
    for( size_t it=0; it < getSize() ; ++it )
      {run_sum += getData(it);}
    return run_sum;
  }

  inline _Tp min() const
  {
    _Tp min_val = std::numeric_limits<_Tp>::max();
    for( size_t it=0; it < getSize() ; ++it )
      if (getData( it ) < min_val) min_val = getData(it);
    return min_val;
  }

  inline _Tp max() const
  {
    _Tp max_val = std::numeric_limits<_Tp>::min();
    for( size_t it=0; it < getSize() ; ++it )
      if (getData( it ) > max_val) max_val = getData(it);
    return max_val;
  }

  inline void normalize() const
  {
    _Tp min_val = this->min();
    _Tp diff_val = this->max() -min_val;
    for( size_t it=0; it < getSize() ; ++it )
      getData(it) = (getData(it) -min_val) /diff_val;
  }

  inline void getGradField( VolumeBase<utils::CoordinateD>& grads, const size_t& window_size=1 ) const
  {
    grads.fill( utils::Coordinate( 0,0,0 ) );
    for( size_t x=1 ; x < m_shape.x()-1 ; ++x )
      for( size_t y=1 ; y < m_shape.y()-1 ; ++y )
        for( size_t z=1 ; z < m_shape.z()-1 ; ++z )
        {
          utils::CoordinateD& cur_grad = grads( x,y,z );
          cur_grad.x() = 0.5*( operator()( x+1,y,z )-operator()( x-1,y,z ) );
          cur_grad.y() = 0.5*( operator()( x,y+1,z )-operator()( x,y-1,z ) );
          cur_grad.z() = 0.5*( operator()( x,y,z+1 )-operator()( x,y,z-1 ) );
        }
    for( size_t it_win_size=1 ; it_win_size < window_size-1 ; ++it_win_size )
    {
      for( size_t x=1 ; x < m_shape.x()-it_win_size ; ++x )
        for( size_t y=1 ; y < m_shape.y()-it_win_size ; ++y )
          for( size_t z=1 ; z < m_shape.z()-it_win_size ; ++z )
          {
            utils::CoordinateD& cur_grad = grads( x,y,z );
            cur_grad.x() = 0.5*( operator()( x+1,y,z )-operator()( x-1,y,z ) );
            cur_grad.y() = 0.5*( operator()( x,y+1,z )-operator()( x,y-1,z ) );
            cur_grad.z() = 0.5*( operator()( x,y,z+1 )-operator()( x,y,z-1 ) );
          }
    }
  }


  inline void resetAccess() { m_access_iter = 0; }
  inline const int getNextAccessIter()
  {
    std::unique_lock<std::mutex> iter_lock( m_access_lock );
    int return_val = m_access_iter;
    ++m_access_iter;
    return return_val;
  }
  inline const int multithreadAccess()
  {
    if( m_access_iter < m_shape[2] )
      return getNextAccessIter();
    else
      return -1;
  }
  inline const int multithreadAccessOffset( const size_t off )
  {
    if( m_access_iter < m_shape[2]-(2*off) )
      return getNextAccessIter()+off;
    else
      return -1;
  }

  inline std::string toString() const
  {
    std::stringstream sstr;
    for( size_t z_it=0; z_it < m_shape[2] ; ++z_it )
    {
      for( size_t y_it=0; y_it < m_shape[1] ; ++y_it )
      {
        for( size_t x_it=0; x_it < m_shape[0] ; ++x_it )
          sstr << getData(getIndex(x_it,y_it,z_it)) << ", ";
        sstr << "\n";
      }
      sstr << "-----\n";
    }
    return sstr.str();
  }

  inline std::string params() const
  {
    std::stringstream sstr;
    sstr << m_shape << std::endl << "Size: " << m_size << std::endl;
    sstr << "ZStep: " << m_z_step << std::endl << m_data.get() << std::endl;
    return sstr.str();
  }

  inline size_t getIndex( const size_t x, const size_t y, const size_t z ) const
  {
    return m_z_step *z +m_shape[0] *y +x;
  }

  inline utils::Coordinate fromIndex( const size_t& idx )
  {
    int z = idx /m_z_step;
    int rem = idx %m_z_step;
    int y = rem /m_shape[1];
    int x = rem %m_shape[1];
    return utils::Coordinate( x,y,z );
  }



  inline void drawLine( const utils::Coordinate& p1, const utils::Coordinate& p2, const _Tp& val )
  {
    utils::GridLine line( p1, p2 );

    const int max_x = std::abs( p1[0] -p2[0] );
    const int max_y = std::abs( p1[1] -p2[1] );
    const int max_z = std::abs( p1[2] -p2[2] );
    if( max_x > max_y && max_x > max_z )
      for( int x=0; x < max_x; ++x )
        operator()( line.x( x ) ) = val;
    else if( max_y > max_z )
      for( int y=0; y < max_y; ++y )
        operator()( line.y( y ) ) = val;
    else
      for( int z=0; z < max_z; ++z )
        operator()( line.z( z ) ) = val;
  }


private:
  //template <class _Tp>
  //inline _Tp forEach( _Tp (*func)() )

  utils::Coordinate m_shape;
  size_t m_z_step;
  size_t m_size;
  std::shared_ptr<ArrayController<_Tp>> m_data;
  bool m_ptr_deprecated = false;

  std::mutex m_access_lock;
  int m_access_iter = 0;

};

typedef VolumeBase<float> Volume;
typedef VolumeBase<double> VolumeD;
typedef VolumeBase<int> VolumeI;
typedef VolumeBase<utils::CoordinateD> Volume3D;

template<class _Tp> void voidPtrToVolume( const void* input, const utils::Coordinate& shape, VolumeBase<_Tp>& output )
{
  output = VolumeBase<_Tp>( shape );
  output = reinterpret_cast<_Tp*>( input );
}

inline std::ostream& operator<<( std::ostream& _ostr, const Volume& _obj )
{
  return _ostr << _obj.toString();
}

inline std::ostream& operator<<( std::ostream& _ostr, const VolumeD& _obj )
{
  return _ostr << _obj.toString();
}

inline std::ostream& operator<<( std::ostream& _ostr, const VolumeI& _obj )
{
  return _ostr << _obj.toString();
}

#endif // VOLUME_H__
