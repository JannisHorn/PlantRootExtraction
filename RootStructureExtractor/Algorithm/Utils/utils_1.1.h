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
    CoordinateBase() = default;

    CoordinateBase( const _Tp x, const _Tp y, const _Tp z )
    {
        coor[0] = x;
        coor[1] = y;
        coor[2] = z;
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
    {
      coor[0] = other[0];
      coor[1] = other[1];
      coor[2] = other[2];
    }

    CoordinateBase( const _Tp* arr )
    {
      coor[0] = arr[0];
      coor[1] = arr[1];
      coor[2] = arr[2];
    }

    inline size_t getSqrdDistance( const CoordinateBase<_Tp>& _c ) const
    {
        return std::pow( coor[0]-_c.coor[0], 2 ) +
               std::pow( coor[1]-_c.coor[1], 2 ) +
               std::pow( coor[2]-_c.coor[2], 2 );
    }

    template <typename _TpA>
    inline double getDistance( const CoordinateBase<_TpA>& _c ) const
    {
        return std::sqrt( std::pow( coor[0]-_c.coor[0], 2 ) +
               std::pow( coor[1]-_c.coor[1], 2 ) +
               std::pow( coor[2]-_c.coor[2], 2 ) );
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp>& operator-( const CoordinateBase<_TpA>& _c )
    {
        coor[0] -= _c[0];
        coor[1] -= _c[1];
        coor[2] -= _c[2];
        return *this;
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp>& operator+( const CoordinateBase<_TpA>& _c )
    {
        coor[0] += _c[0];
        coor[1] += _c[1];
        coor[2] += _c[2];
        return this;
    }

    template <typename _TpA>
    inline CoordinateBase<_Tp> operator+( const _TpA& _scalar )
    {
        CoordinateBase<_Tp> out;
        out[0] = coor[0] + _scalar;
        out[1] = coor[1] + _scalar;
        out[2] = coor[2] + _scalar;
        return out;
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
        return this;
    }

    inline _Tp& operator[]( const size_t _it )
    {
        return coor[_it];
    }

    inline const _Tp& operator[]( const size_t _it ) const
    {
        return coor[_it];
    }

    inline _Tp getMean() const
    {
        return ( coor[0] +coor[1] +coor[2] ) /3;
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
        coor[0] = _c.coor[0];
        coor[1] = _c.coor[1];
        coor[2] = _c.coor[2];
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

    inline CoordinateBase<_Tp> addElem( const _Tp& val, const int& id ) const
    {
      CoordinateBase<_Tp> new_coor( coor[0], coor[1], coor[2] );
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

    _Tp coor[3];
};

typedef CoordinateBase<int> Coordinate;
typedef CoordinateBase<double> CoordinateD;
typedef CoordinateBase<float> CoordinateF;

}

inline std::ostream& operator<<( std::ostream& _ostr, const utils::Coordinate& _obj )
{
    return _ostr << _obj.toString();
}

inline std::ostream& operator<<( std::ostream& _ostr, const utils::CoordinateD& _obj )
{
    return _ostr << _obj.toString();
}

#endif // NPY_UTILS_H_
