/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef NEIGHBORHOOD_H__
#define NEIGHBORHOOD_H__

#include <vector>
#include "utils.h"
#include <cmath>
#include <bitset>

namespace utils
{

struct NeighborhoodBase
{
public:
  struct ModifyNode
  {
    ModifyNode() : pred( 0 ), mult( 1 ) {};
    ModifyNode( const Coordinate& n_pos, const float& n_mult, const int& n_pred )
     : pos( n_pos ), pred( n_pred ), mult( n_mult ) {}

    ModifyNode( const ModifyNode& other, const int& val, const int& id, const float& n_mult, const int& n_pred )
     : pos( other.pos.addElem( val, id ) ), mult( other.mult *n_mult ), pred( other.pred + n_pred ) {}

    inline void modify( const int& val=0, const int& id=0, const float& n_mult=1, const int& n_pred=0 )
    {
      pos.addInPos( val, id );
      mult *= n_mult;
      pred += n_pred; //kept as "+" for consistency
    }

    inline void modify( const Coordinate& n_pos, const float& n_mult=1, const int& n_pred=0 )
    {
      pos = n_pos;
      mult = n_mult;
      pred = n_pred; //kept as "+" for consistency
    }

    inline std::string toString() const
    {
      std::stringstream sstr;
      sstr << "(" << pos << ", " << mult << ", " << pred << ")" << std::endl;
      return sstr.str();
    }

    Coordinate pos;
    float mult;
    int pred;
  };
  typedef std::vector<ModifyNode> NodeVector;
  typedef std::bitset<sizeof(int)*8> IntBits;

  NeighborhoodBase( const Coordinate& shape, const CoordinateF& mults, const size_t& max_size ) : m_shape( shape ), m_mults( mults ), m_max_size( max_size ) {};
  virtual inline size_t operator()( const Coordinate& pos, NodeVector& out ) = 0;
  virtual inline Coordinate operator()( const Coordinate& pos, const int& pred_code ) const = 0;
  inline size_t getMaxSize() const { return m_max_size; }

  inline int comparePredecessors( const int& cur_pred, const int& neighbor_pred  ) const
  {
    IntBits cur( cur_pred ), neigh( -neighbor_pred );
    utils::Coordinate pred_vec(0,0,0), neigh_vec(0,0,0);
    vecFromBitSet( cur, pred_vec );
    vecFromBitSet( neigh, neigh_vec );
    return pred_vec.dotProduct( neigh_vec );
  }

  inline utils::CoordinateD getVector( const int& pred ) const
  {
    utils::CoordinateD vec;
    vecFromBitSet( IntBits( pred ), vec );
    return vec;
  }
protected:
  inline void addNode( NodeVector& out, const Coordinate& n_pos, const float& n_mult, const int& n_pred )
  {
    out[m_it].modify( n_pos, n_mult, n_pred );
    ++m_it;
  }

  template<typename _Tp>
  inline void vecFromBitSet( const IntBits& cur, utils::CoordinateBase<_Tp>& out ) const
  {
    if( cur[0] ) out[0] = -1;
    else if( cur[1] ) out[0] = 1;

    if( cur[2] ) out[1] = -1;
    else if( cur[3] ) out[1] = 1;

    if( cur[4] ) out[2] = -1;
    else if( cur[5] ) out[2] = 1;
  }

  const Coordinate m_shape;
  const CoordinateF m_mults;
  size_t m_it = 0, m_max_size;
};


struct NeighborhoodID1 : public NeighborhoodBase
{
  NeighborhoodID1( const Coordinate& shape, const CoordinateF& mults )
    : NeighborhoodBase( shape, mults, 6 ) {};

  inline size_t operator()( const Coordinate& pos, NodeVector& out ) override
  {
    out.clear();
    utils::Coordinate n_pos = pos;
    if( pos[0] > 0 )
      out.push_back( ModifyNode( n_pos.addElem( -1, 0 ), m_mults[0], -32 ) );
    if( pos[0] < m_shape[0] -1 )
      out.push_back( ModifyNode( n_pos.addElem( 1, 0 ), m_mults[0], -16 ) );
    if( pos[1] > 0 )
      out.push_back( ModifyNode( n_pos.addElem( -1, 1 ), m_mults[1], -8 ) );
    if( pos[1] < m_shape[1] -1 )
      out.push_back( ModifyNode( n_pos.addElem( 1, 1 ), m_mults[1], -4 ) );
    if( pos[2] > 0 )
      out.push_back( ModifyNode( n_pos.addElem( -1, 2 ), m_mults[2], -2 ) );
    if( pos[2] < m_shape[2] -1 )
      out.push_back( ModifyNode( n_pos.addElem( 1, 2 ), m_mults[2], -1 ) );
    return out.size();
  }

  inline Coordinate operator()( const Coordinate& pos, const int& pred_code ) const override
  {
    Coordinate n_pos = pos;
    switch( pred_code )
    {
      case 32: return n_pos.addElem( 1,0 );
      case 16: return n_pos.addElem( -1,0 );
      case 8: return n_pos.addElem( 1,1 );
      case 4: return n_pos.addElem( -1,1 );
      case 2: return n_pos.addElem( 1,2 );
      case 1: return n_pos.addElem( -1,2 );
      default: return pos;
    }
  }
};



struct NeighborhoodID2 : public NeighborhoodBase
{
  NeighborhoodID2( const Coordinate& shape, const CoordinateF& mults )
    : NeighborhoodBase( shape, mults, 18 ) {};

  inline size_t operator()( const Coordinate& pos, std::vector<ModifyNode>& out ) override
  {
    out.clear();
    utils::Coordinate n_pos = pos;
    if( pos[0] > 0 )
    {
      int idd = 1;
      ModifyNode node( n_pos.addElem( -1, 0 ), m_mults[0], -32 );
      forY( pos, out, node, idd );
    }
    {
      int idd = 0;
      ModifyNode node( n_pos, 1, 0 );
      forY( pos, out, node, idd );
    }
    if( pos[0] < m_shape[0] -1 )
    {
      int idd = 1;
      ModifyNode node( n_pos.addElem( 1, 0 ), m_mults[0], -16 );
      forY( pos, out, node, idd );
    }
    return out.size();
  }

  inline void forY( const Coordinate& pos, std::vector<ModifyNode>& out,
                    ModifyNode node, int& idd ) const
  {
    if( pos[1] > 0 )
    {
      ModifyNode n_node( node, -1, 1, m_mults[1], -8 );
      forZ( pos, out, n_node, ++idd );
    }
    forZ( pos, out, node, idd );
    if( pos[1] < m_shape[1] -1 )
    {
      ModifyNode n_node( node, 1, 1, m_mults[1], -4 );
      forZ( pos, out, n_node, ++idd );
    }
  }

  inline void forZ( const Coordinate& pos, std::vector<ModifyNode>& out,
                    ModifyNode node, int& idd ) const
  {//TODO fix node
    if( idd == 0 ) {
      if( pos[2] > 0 )
        out.push_back( ModifyNode( node, -1, 2, m_mults[2], -2 ) );
      if( pos[2] < m_shape[2] -1 )
        out.push_back( ModifyNode( node, 1, 2, m_mults[2], -1 ) );
    }
    else if( idd == 1 )
    {
      if( pos[2] > 0 )
        out.push_back( ModifyNode( node, -1, 2, m_mults[2] *sqrt_2, -2 ) );
      out.push_back( node );
      if( pos[2] < m_shape[2] -1 )
        out.push_back( ModifyNode( node, 1, 2, m_mults[2] *sqrt_2, -1 ) );
    }
    else if( idd == 2 )
      out.push_back( ModifyNode( node, 0, 0, 1*sqrt_2, 0 ) );
  }


  inline Coordinate operator()( const Coordinate& pos, const int& pred_code ) const override
  {
    Coordinate n_pos = pos;
    IntBits pred_bit( pred_code );
    if( pred_bit[5] ) n_pos.addInPos( 1, 0 );
    else if( pred_bit[4] ) n_pos.addInPos( -1, 0 );
    if( pred_bit[3] ) n_pos.addInPos( 1, 1 );
    else if( pred_bit[2] ) n_pos.addInPos( -1, 1 );
    if( pred_bit[1] ) n_pos.addInPos( 1, 2 );
    else if( pred_bit[0] ) n_pos.addInPos( -1, 2 );
    return n_pos;
  }

private:
  constexpr static float sqrt_2 = sqrt(2);
};


struct NeighborhoodID3 : public NeighborhoodBase
{
  NeighborhoodID3( const Coordinate& shape, const CoordinateF& mults )
      : NeighborhoodBase( shape, mults, 26 ) {};

  inline size_t operator()( const Coordinate& pos, std::vector<ModifyNode>& out ) override
  {
    out.clear();
    utils::Coordinate n_pos = pos;
    if( pos[0] > 0 )
    {
      int idd = 1;
      ModifyNode node( n_pos.addElem( -1, 0 ), m_mults[0], -32 );
      forY( pos, out, node, idd );
    }
    {
      int idd = 0;
      ModifyNode node( n_pos, 1, 0 );
      forY( pos, out, node, idd );
    }
    if( pos[0] < m_shape[0] -1 )
    {
      int idd = 1;
      ModifyNode node( n_pos.addElem( 1, 0 ), m_mults[0], -16 );
      forY( pos, out, node, idd );
    }
    return out.size();
  }

  inline void forY( const Coordinate& pos, std::vector<ModifyNode>& out,
                    ModifyNode node, int& idd ) const
  {
    if( pos[1] > 0 )
    {
      ModifyNode n_node( node, -1, 1, m_mults[1], -8 );
      forZ( pos, out, n_node, ++idd );
    }
    forZ( pos, out, node, idd );
    if( pos[1] < m_shape[1] -1 )
    {
      ModifyNode n_node( node, 1, 1, m_mults[1], -4 );
      forZ( pos, out, n_node, ++idd );
    }
  }

  inline void forZ( const Coordinate& pos, std::vector<ModifyNode>& out,
                    ModifyNode node, int& idd ) const
  {//TODO fix node
    if( idd == 0 ) {
      if( pos[2] > 0 )
        out.push_back( ModifyNode( node, -1, 2, m_mults[2], -2 ) );
      if( pos[2] < m_shape[2] -1 )
        out.push_back( ModifyNode( node, 1, 2, m_mults[2], -1 ) );
    }
    else if( idd == 1 )
    {
      if( pos[2] > 0 )
        out.push_back( ModifyNode( node, -1, 2, m_mults[2] *sqrt_2, -2 ) );
      out.push_back( node );
      if( pos[2] < m_shape[2] -1 )
        out.push_back( ModifyNode( node, 1, 2, m_mults[2] *sqrt_2, -1 ) );
    }
    else if( idd == 2 )
    {
      if( pos[2] > 0 )
        out.push_back( ModifyNode( node, -1, 2, m_mults[2] *sqrt_3, -2 ) );
      out.push_back( ModifyNode( node, 0, 0, 1*sqrt_2, 0 ) );
      if( pos[2] < m_shape[2] -1 )
        out.push_back( ModifyNode( node, 1, 2, m_mults[2] *sqrt_3, -1 ) );
    }
  }


  inline Coordinate operator()( const Coordinate& pos, const int& pred_code ) const override
  {
    Coordinate n_pos = pos;
    IntBits pred_bit( pred_code );
    if( pred_bit[5] ) n_pos.addInPos( 1, 0 );
    else if( pred_bit[4] ) n_pos.addInPos( -1, 0 );
    if( pred_bit[3] ) n_pos.addInPos( 1, 1 );
    else if( pred_bit[2] ) n_pos.addInPos( -1, 1 );
    if( pred_bit[1] ) n_pos.addInPos( 1, 2 );
    else if( pred_bit[0] ) n_pos.addInPos( -1, 2 );
    return n_pos;
  }

private:
  constexpr static float sqrt_2 = sqrt(2);
  constexpr static float sqrt_3 = sqrt(3);

};

}
#endif // NEIGHBORHOOD_H__

