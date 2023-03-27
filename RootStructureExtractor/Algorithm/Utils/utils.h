/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef NPY_UTILS_H_
#define NPY_UTILS_H_

#include <memory>
#include <time.h>
#include <cstdlib>
#include <exception>
#include <cmath>
#include <vector>
#include <sstream>
#include <ostream>
#include <iostream>
#include <random>
#include <chrono>

extern std::default_random_engine g_rand;

namespace utils
{

inline void strToNum( const std::string& _arg, size_t& _val )
{
    _val = static_cast<size_t>( std::stoi( _arg ) );
}

inline void strToNum( const std::string& _arg, double& _val )
{
    _val = std::stof( _arg );
}

template<typename _Tp>
struct CoordinateBase
{
  private:
    struct Data
    {
      Data() = default;
      Data( const _Tp& n_x, const _Tp& n_y, const _Tp& n_z ) : x(n_x), y(n_y), z(n_z) {}
      Data( const Data& other ) : x( other.x ), y( other.y ), z( other.z ) {}
      void operator=( const Data& other ) { x = other.x; y = other.y; z = other.z; }

      _Tp x,y,z;
    };
  public:
    CoordinateBase() = default;

    CoordinateBase( const _Tp x, const _Tp y, const _Tp z )
      : data( x,y,z )
    {
        //coor[0] = x;
        //coor[1] = y;
        //coor[2] = z;
    }

    CoordinateBase( const std::vector<_Tp>& _input )
    {
        coor[0] = _input[0];
        coor[1] = _input[1];
        if( _input.size() == 3 )
            coor[2] = _input[2];
        else
            coor[2] = 0;
    }

    CoordinateBase( const CoordinateBase<_Tp>& other )
      : data( other.data )
    {
      //data.x = other[0];
      //data.y = other[1];
      //data.z = other[2];
    }

    template<typename _TpA>
    CoordinateBase( const CoordinateBase<_TpA>& other )
      : data( _Tp( other[0] ), _Tp( other[1] ), _Tp( other[2] ) ) {}

    CoordinateBase( const _Tp* arr )
    {
      coor[0] = arr[2];
      coor[1] = arr[1];
      coor[2] = arr[0];
    }

    inline const _Tp& x() const { return data.x; }
    inline _Tp& x() { return data.x; }
    inline const _Tp& y() const { return data.y; }
    inline _Tp& y() { return data.y; }
    inline const _Tp& z() const { return data.z; }
    inline _Tp& z() { return data.z; }

    inline double normSqrd() const
    {
      return std::pow( x(), 2 ) +std::pow( y(), 2 ) +std::pow( z(), 2 );
    }

    inline double norm() const
    {
      return std::sqrt( normSqrd() );
    }

    inline size_t getSqrdDistance( const CoordinateBase<_Tp>& _c ) const
    {
        return std::pow( coor[0]-_c.coor[0], 2 ) +
               std::pow( coor[1]-_c.coor[1], 2 ) +
               std::pow( coor[2]-_c.coor[2], 2 );
    }

    inline double getSqrdDistance( const CoordinateBase<_Tp>& _c, const CoordinateBase<float>& mults ) const
    {
        return std::pow( ( coor[0]-_c.coor[0] ) *mults[0], 2 ) +
               std::pow( ( coor[1]-_c.coor[1] ) *mults[1], 2 ) +
               std::pow( ( coor[2]-_c.coor[2] ) *mults[2], 2 );
    }

    template <typename _TpA>
    inline double getDistance( const CoordinateBase<_TpA>& _c ) const
    {
        return std::sqrt( std::pow( coor[0]-_c.coor[0], 2 ) +
               std::pow( coor[1]-_c.coor[1], 2 ) +
               std::pow( coor[2]-_c.coor[2], 2 ) );
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp> operator-( const CoordinateBase<_TpA>& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] -_c[0];
        out[1] = coor[1] -_c[1];
        out[2] = coor[2] -_c[2];
        return out;
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp>& scalarDiff( const _TpA& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] -_c;
        out[1] = coor[1] -_c;
        out[2] = coor[2] -_c;
        return out;
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp> scalarSum( const CoordinateBase<_TpA>& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] +_c[0];
        out[1] = coor[1] +_c[1];
        out[2] = coor[2] +_c[2];
        return out;
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp> scalarMult( const CoordinateBase<_TpA>& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] *_c[0];
        out[1] = coor[1] *_c[1];
        out[2] = coor[2] *_c[2];
        return out;
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp> operator+( const _TpA& _scalar ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] + _scalar;
        out[1] = coor[1] + _scalar;
        out[2] = coor[2] + _scalar;
        return out;
    }
    inline CoordinateBase<_Tp> operator+( const CoordinateBase<_Tp>& _other ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] + _other[0];
        out[1] = coor[1] + _other[1];
        out[2] = coor[2] + _other[2];
        return out;
    }
    inline CoordinateBase<_Tp>& operator+=( const _Tp& _scalar )
    {
        coor[0] += _scalar;
        coor[1] += _scalar;
        coor[2] += _scalar;
        return *this;
    }
    inline CoordinateBase<_Tp>& operator+=( const CoordinateBase<_Tp>& _other )
    {
        coor[0] += _other.coor[0];
        coor[1] += _other.coor[1];
        coor[2] += _other.coor[2];
        return *this;
    }

    template <typename _TpOut, typename _TpA>
    inline CoordinateBase<_TpOut> mult( const _TpA& _scalar ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] * _scalar;
        out[1] = coor[1] * _scalar;
        out[2] = coor[2] * _scalar;
        return out;
    }
    inline CoordinateBase<double> operator*( const double scalar ) const { return mult<double, double>( scalar ); }
    inline CoordinateBase<double> operator*( const float scalar ) const { return mult<double, float>( scalar ); }
    template <typename _TpA> inline CoordinateBase<_Tp> operator*( const _TpA scalar ) const { return mult<_Tp, _TpA>( scalar ); }

    inline CoordinateBase<_Tp> operator*( const CoordinateBase<_Tp>& _other ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] * _other[0];
        out[1] = coor[1] * _other[1];
        out[2] = coor[2] * _other[2];
        return out;
    }

    inline CoordinateBase<_Tp>& operator*=( const CoordinateBase<_Tp>& _other )
    {
        coor[0] *= _other[0];
        coor[1] *= _other[1];
        coor[2] *= _other[2];
        return *this;
    }


    inline bool operator==( const CoordinateBase<_Tp>& _coord ) const
    {
        return  coor[0] == _coord.coor[0] &&
                coor[1] == _coord.coor[1] &&
                coor[2] == _coord.coor[2];
    }
    inline bool operator!=( const CoordinateBase<_Tp>& _coord ) const
    {
        return !operator==( _coord );
    }

    inline CoordinateBase<_Tp>& elemwiseMult( const CoordinateBase<_Tp>& _c )
    {
        coor[0] *= _c[0];
        coor[1] *= _c[1];
        coor[2] *= _c[2];
        return *this;
    }

    inline CoordinateBase<_Tp>& elemwiseDiff( const CoordinateBase<_Tp>& _c )
    {
        coor[0] /= _c[0];
        coor[1] /= _c[1];
        coor[2] /= _c[2];
        return *this;
    }

    inline CoordinateBase<_Tp> crossProduct( const CoordinateBase<_Tp>& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = y() *_c.z() -( z() *_c.y() );
        out[1] = z() *_c.x() -( x() *_c.z() );
        out[2] = x() *_c.y() -( y() *_c.x() );
        return out;
    }

    inline CoordinateBase<_Tp> scale( const double& _scale ) const
    {
        CoordinateBase<_Tp> out;
        out.data.x = data.x *_scale;
        out.data.y = data.y *_scale;
        out.data.z = data.z *_scale;
        return out;
    }

    inline CoordinateBase<_Tp> scalarMax( const CoordinateBase<_Tp>& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = std::max( data.x, _c.x() );
        out[1] = std::max( data.y, _c.y() );
        out[2] = std::max( data.z, _c.z() );
        return out;
    }

    inline CoordinateBase<_Tp> scalarMin( const CoordinateBase<_Tp>& _c ) const
    {
        CoordinateBase<_Tp> out;
        out[0] = std::min( data.x, _c.x() );
        out[1] = std::min( data.y, _c.y() );
        out[2] = std::min( data.z, _c.z() );
        return out;
    }

    inline CoordinateBase<int> toInt() const
    {
      CoordinateBase<int> out;
      out.x() = std::round( x() );
      out.y() = std::round( y() );
      out.z() = std::round( z() );
      return out;
    }

    inline _Tp& operator[]( const size_t _it )
    {
        return coor[_it];
    }

    inline const _Tp& operator[]( const size_t _it ) const
    {
        return coor[_it];
    }

    inline const _Tp min() const
    {
      _Tp min_elem = std::min( data.x, data.y );
      return std::min( min_elem, data.z );
    }

    inline const _Tp max() const
    {
      _Tp max_elem = std::max( data.x, data.y );
      return std::max( max_elem, data.z );
    }

    inline _Tp getMean() const
    {
        return ( coor[0] +coor[1] +coor[2] ) /3;
    }

    inline int argmax() const
    {
      int argm = 0;
      if( coor[0] < coor[1] )
        argm = 1;
      if( coor[argm] < coor[2] )
        argm = 2;
      return argm;
    }

    inline void operator=( const std::string& _vals )
    {
        if( _vals[0] != '[' || _vals[_vals.size() -1] != ']' )
            throw std::runtime_error( "Range: fromString(): Wrong format. Expected \"[...]\" " );

        std::string proto_data_size = _vals.substr( 1, _vals.size() -1 );
        int it = 0; size_t pos = 0;
        do {
            pos = proto_data_size.find(",");
            std::string val = proto_data_size.substr(0, pos);
            coor[it] = std::stoi( val );
            ++it;
            proto_data_size.erase( 0, pos+1 );
        } while ( pos != std::string::npos );
    }

    inline void operator=( const CoordinateBase<_Tp>& _c )
    {
        data = _c.data;
    }

    inline void normalize( )
    {
        double length = std::sqrt( std::pow( coor[0], 2 ) +std::pow( coor[1], 2 ) +std::pow( coor[2], 2 ) );
        if( length == 0 )
            return;
        coor[0] /= length;
        coor[1] /= length;
        coor[2] /= length;
        //std::cout << length << " from " << toString() << std::endl;
    }

    inline _Tp dotProduct( const CoordinateBase<_Tp>& _c ) const
    {
        return coor[0]*_c[0] +coor[1]*_c[1] +coor[2]*_c[2];
    }

    inline double getAngle( const CoordinateBase<_Tp>& _c ) const
    {
      _Tp scalar = dotProduct( _c );
      double n1 = norm(), n2 = _c.norm();
      return acos( scalar/(n1*n2) );
    }

    inline double getPlaneAngle( const CoordinateBase<_Tp>& _normal ) const
    {
      _Tp scalar = dotProduct( _normal );
      double n1 = norm(), n2 = _normal.norm();
      return asin( scalar/(n1*n2) );
    }

    inline CoordinateBase<_Tp> addElem( const _Tp& val, const int& id ) const
    {
      CoordinateBase<_Tp> new_coor( *this );
      new_coor[id] += val;
      return new_coor;
    }

    inline void addInPos( const _Tp& val, const int& id )
    {
      coor[id] += val;
    }

    inline std::string toString() const
    {
        std::stringstream sstr;
        sstr << "[" << coor[0] << "," << coor[1] << "," << coor[2] << "]";
        return sstr.str();
    }

    template <typename _Tp0>
    inline const _Tp0& iter( const std::vector<std::vector<std::vector<_Tp0>>>& _vec ) const
    {
        return _vec[coor[0]][coor[1]][coor[2]];
    }

    template <typename _TpNew>
    inline CoordinateBase<_TpNew> toType() const
    {
      CoordinateBase<_TpNew> out;
      out[0] = coor[0];
      out[1] = coor[1];
      out[2] = coor[2];
      return out;
    }

    union
    {
      _Tp coor[3];
      Data data;
    };
};

typedef CoordinateBase<int> Coordinate;
typedef CoordinateBase<double> CoordinateD;
typedef CoordinateBase<float> CoordinateF;


struct Line
{
  template<typename _TpA>
  Line( const CoordinateBase<_TpA>& p1, const CoordinateBase<_TpA>& p2 )
    : b( p1 ), m( p2-p1 ), len( 1.0 ) {}

  template<typename _TpA>
  inline double distSqrd( const CoordinateBase<_TpA>& point ) const
  {
    double dem = ( point -b ).crossProduct( m ).normSqrd();
    return dem /m.normSqrd();
  }

  template<typename _TpA>
  inline double dist( const CoordinateBase<_TpA>& point ) const
  {
    return std::sqrt( distSqrd( point ) );
  }

  inline void scale( const double& fac )
  {
    m = m*fac;
    len /= fac;
  }

  inline void normalize()
  {
    scale( 1/m.norm() );
  }

  inline virtual utils::CoordinateD operator()( const double& x ) const
  {
    return m*x+b;
  }

  inline std::string toString() const
  {
    std::stringstream sstr;
    sstr << b.toString() << " + " << m.toString() << "*x";
    return sstr.str();
  }

  utils::CoordinateD m;
  utils::CoordinateD b;
  double len;
};


struct ScaledLine : public Line
{
  ScaledLine( const Coordinate& p1, const Coordinate& p2, const CoordinateD& dim_mults )
    : Line( p1, p2 ), mults( dim_mults )
  {
    m = m.elemwiseMult( dim_mults );
  }

  inline utils::CoordinateD operator()( const double& x ) const override
  {
    utils::CoordinateD pt = m*x;
    //std::cout << "DEB: Scaled out: " << pt.toString() << "/" << mults.toString() << "=" << pt.elemwiseDiff(mults).toString() << std::endl;
    return pt.elemwiseDiff( mults )+b;
  }

private:
  const utils::CoordinateD& mults;
};


struct GridLine : public Line
{
  GridLine( const Coordinate& p1, const Coordinate& p2 )
    : Line( p1, p2 )
  {
    per[0] = 1.0 /std::abs( p1[0] -p2[0] );
    per[1] = 1.0 /std::abs( p1[1] -p2[1] );
    per[2] = 1.0 /std::abs( p1[2] -p2[2] );
  }

  inline utils::Coordinate x( const int& it ) const
  {
    return atRel( it, 0 );
  }
  inline utils::Coordinate y( const int& it ) const
  {
    return atRel( it, 1 );
  }
  inline utils::Coordinate z( const int& it ) const
  {
    return atRel( it, 2 );
  }

  inline utils::Coordinate atRel( const int& it, const int& dim ) const
  {
    double cur_per = per[dim] *it;
    utils::Coordinate out;
    out[0] = std::round( cur_per *m[0] +b[0] );
    out[1] = std::round( cur_per *m[1] +b[1] );
    out[2] = std::round( cur_per *m[2] +b[2] );
    return out;
  }

  inline utils::Coordinate atAbs( const int& it, const int& dim ) const
  {
    return atRel( it -b[0], dim );
  }

  utils::CoordinateD per;
};


template<typename _Tp>
struct AlignedBox
{
  AlignedBox( const CoordinateBase<_Tp>& p1, const CoordinateBase<_Tp>& p2 )
  {
    mins = p1.scalarMin( p2 );
    maxs = p1.scalarMax( p2 );
  }

  void enlarge( const _Tp& adt )
  {
    mins -= adt;
    maxs += adt;
  }

  bool overlap( const AlignedBox<_Tp>& other ) const
  {
    if( mins[0] <= other.maxs[0] && maxs[0] >= other.mins[0] )
      if( mins[1] <= other.maxs[1] && maxs[1] >= other.mins[1] )
        if( mins[2] <= other.maxs[2] && maxs[2] >= other.mins[2] )
          return true;
    return false;
  }

  utils::CoordinateBase<_Tp> mins;
  utils::CoordinateBase<_Tp> maxs;
};
typedef AlignedBox<double> AlignedBoxD;
typedef AlignedBox<int> AlignedBoxI;


}

inline std::ostream& operator<<( std::ostream& _ostr, const utils::Coordinate& _obj )
{
    return _ostr << _obj.toString();
}

inline std::ostream& operator<<( std::ostream& _ostr, const utils::CoordinateD& _obj )
{
    return _ostr << _obj.toString();
}

inline std::ostream& operator<<( std::ostream& _ostr, const utils::CoordinateF& _obj )
{
    return _ostr << _obj.toString();
}

inline std::ostream& operator<<( std::ostream& _ostr, const utils::Line& _obj )
{
    return _ostr << _obj.toString();
}
#endif // NPY_UTILS_H_
