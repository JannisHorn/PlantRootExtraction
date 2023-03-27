/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef ADAPTED_DJIKSTRA_H__
#define ADAPTED_DJIKSTRA_H__

#include "utils.h"
#include "volume.h"
#include "fibonacci_heap.h"
#include "neighborhood.h"
#include <functional>

#include <queue>

class DjikstraBase
{
public:
  struct Node
  {
    utils::Coordinate coor;
    int pred;
    double cost;

    Node() {}
    Node( const int& x, const int& y, const int& z, const int& n_pred ) :
      coor( utils::Coordinate( x,y,z ) ), pred( n_pred ) {}
    Node( const utils::Coordinate& n_coor, const int& n_pred ) :
      coor( n_coor ), pred( n_pred ) {}

    Node( const utils::Coordinate& n_coor, const int& n_pred, const double& n_cost ) :
      coor( n_coor ), pred( n_pred ), cost( n_cost ) {}
    Node( const Node& other ) :
      coor( other.coor ), pred( other.pred ), cost( other.cost ) {}
  };

public:
  DjikstraBase( const Volume& input,
                Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map, const int idd,
                const float cost_cutoff, const utils::CoordinateF& mults );
  ~DjikstraBase();
  void operator()( const utils::Coordinate& start_node );
  void initShortestPath( const utils::Coordinate& start_node );
  void shortestPath();

protected:
  inline bool nodeVisited( const Node& node ) const
  {
    return nodeVisited( node.coor );
  }
  inline bool nodeVisited( const utils::Coordinate& coor ) const
  {
    return m_pred_map_1( coor ) > 0 ;
  }

  inline void visitNode( const utils::Coordinate& coor )
  {
    m_pred_map_1( coor ) *= -1;
    m_pred_map_2( coor ) *= -1;
  }

  virtual void updateNeighborhood( const utils::Coordinate& coor, const float& cost ) {};


  inline void updateNeighbor( const utils::Coordinate& coor, const float& cost, const float& cost_mult, const int& pred )
  {
    if( nodeVisited( coor ) )
      return;
    float new_cost = cost + ( m_input( coor ) *cost_mult );
    if( new_cost > m_cost_cutoff )
      return;
    //new_cost = coor[0];
    updateCostMaps( coor, new_cost, pred );
  }

  inline void updateCostMaps( const utils::Coordinate& coor, const float& new_cost, const int& pred  )
  {
    float& cost_2 = m_cost_map_2( coor );
    float& cost_1 = m_cost_map_1( coor );
    int& pred_2 = m_pred_map_2( coor );
    int& pred_1 = m_pred_map_1( coor );
    if( cost_2 > new_cost )
    {
      if( cost_1 > new_cost )
      {
        cost_2 = cost_1;
        cost_1 = new_cost;
        pred_2 = pred_1;
        pred_1 = pred;
        //m_unvisited_nodes.insert( new_cost, Node( coor, pred ) );
        m_unvisited_nodes.push( Node( coor, pred, new_cost ) );
      }
      else
      {
        cost_2 = new_cost;
        pred_2 = pred;
      }
    }
  }

  inline void updateNode( const utils::Coordinate& coor, const float& cost )
  {
    visitNode( coor );
    updateNeighborhood( coor, cost );
  }

  const Volume &m_input;
  Volume &m_cost_map_1, &m_cost_map_2;
  VolumeI &m_pred_map_1, &m_pred_map_2;
  utils::Coordinate m_shape;
  //utils::FibonacciHeap<Node> m_unvisited_nodes;
  std::priority_queue<Node, std::vector<Node>, std::greater<Node> > m_unvisited_nodes;
  size_t m_num_elems;
  float m_cost_cutoff;
  utils::NeighborhoodBase* m_neighbor;
  std::vector<utils::NeighborhoodBase::ModifyNode> m_mod_nodes;
};

inline bool operator>( const DjikstraBase::Node& n1, const DjikstraBase::Node& n2 ) { return n1.cost > n2.cost; }




class AdaptedDjikstra : public DjikstraBase
{
public:
  AdaptedDjikstra( const Volume& input,
                   Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                   VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map, const int idd,
                   const float cost_cutoff, const utils::CoordinateF& mults );

protected:
  void updateNeighborhood( const utils::Coordinate& coor, const float& cost ) override
  {
    const size_t vec_size = (*m_neighbor)( coor, m_mod_nodes );
    for( size_t it=0; it < vec_size ; ++it )
    {
      utils::NeighborhoodBase::ModifyNode& cur = m_mod_nodes[it];
      updateNeighbor( cur.pos, cost, cur.mult, cur.pred );
    }
  }//TODO reweigh cost based on distance
};



class AdaptedDjikstraDirectionCost : public DjikstraBase
{
public:
  AdaptedDjikstraDirectionCost( const Volume& input, const Volume& rad_map,
                                Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                                VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map, const int idd,
                                const float cost_cutoff, const utils::CoordinateF& mults,
                                const float dir_penalty_mult );

protected:
  double compareGradient( const int& cur_pred, const utils::Coordinate& coor ) const
  {
    const utils::CoordinateD& cur_grad = m_rad_grads( coor );
    utils::CoordinateD cur_dir = m_neighbor->getVector( cur_pred );
    cur_dir.normalize();
    double w = cur_grad.dotProduct( cur_dir );
    //if( cur_grad != utils::CoordinateD(0.0,0.0,0.0) ) std::cout << "w=" << w << ", dir=" << cur_dir << ", grad=" << cur_grad << std::endl;
    return std::abs( std::min( 0.0, w ) );
  }


  double compareDirection( const int& cur_pred, const int& neighbor_pred ) const
  {
    const int dot_prod = m_neighbor->comparePredecessors( cur_pred, neighbor_pred );
    if ( dot_prod < 0 ) return m_dir_penalty_mult;
    else return 1.0;
  }

  void updateNeighborhood( const utils::Coordinate& coor, const float& cost ) override
  {
    const size_t vec_size = (*m_neighbor)( coor, m_mod_nodes );
    for( size_t it=0; it < vec_size ; ++it )
    {
      utils::NeighborhoodBase::ModifyNode& cur = m_mod_nodes[it];
      double mod = compareDirection( m_pred_map_1( coor ), cur.pred );
      mod += compareGradient( cur.pred, coor );
      updateNeighbor( cur.pos, cost *mod, cur.mult, cur.pred );
    }
  }

  const Volume m_rad_map;
  float m_dir_penalty_mult;
  Volume3D m_rad_grads;
};




class DjikstraWithGapClosing : public DjikstraBase
{
public:
  DjikstraWithGapClosing( const Volume& cost_input,
                          Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                          VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map,
                          VolumeI& n_gap_ident, const int idd,
                          const float cost_cutoff, const utils::CoordinateF& mults,
                          const double cost_part, const int max_gap_length );

protected:
  void updateNeighborhood( const utils::Coordinate& coor, const float& cost ) override
  {
    const size_t vec_size = (*m_neighbor)( coor, m_mod_nodes );
    for( size_t it=0; it < vec_size ; ++it )
    {
      utils::NeighborhoodBase::ModifyNode& cur = m_mod_nodes[it];
      updateNeighbor( cur.pos, cost, cur.mult, cur.pred, m_gap_range( coor ) );
    }
  }


  inline void updateNeighbor( const utils::Coordinate& coor, const float& cost, const float& cost_mult, const int& pred, const int& gap_length )
  {
    if( nodeVisited( coor ) )
      return;
    const float& cur_cost = m_input( coor );
    float edge_cost = cur_cost *cost_mult;
    float new_cost = cost +edge_cost;
    //std::cout << coor << ": Cost=" << new_cost << ", Coor=" << cur_cost << ", Gap=" << gap_length << std::endl;
    if( cur_cost < m_part_cost )
    {
      if( gap_length > 0 && gap_length <= m_gap_length )
      {
        m_gap_range( coor ) = gap_length +cost_mult;
        new_cost = reevaluateGap( coor, cur_cost, pred );
        if( new_cost < m_cost_cutoff )
        {
          m_gap_range( coor ) = 0;
          updateCostMaps( coor, new_cost, pred );
          //updateCostMaps( coor, new_cost -(m_part_cost *gap_length), pred );
        }
      }
      else if( new_cost < m_cost_cutoff )
      {
        m_gap_range( coor ) = 0;
        updateCostMaps( coor, new_cost, pred );
      }
    }
    else if( gap_length < m_gap_length )
    {
      const float& gap_r = m_gap_range( coor );
      if( gap_r > gap_length || gap_r == 0 )
        m_gap_range( coor ) = gap_length +cost_mult;
      updateCostMaps( coor, new_cost, pred );
    }
  }


  inline float reevaluateGap( const utils::Coordinate& coor, const float& cost, const int& pred )
  {
    if( m_gap_range(coor) > 0 )
    {
      const utils::Coordinate pred_coor = (*m_neighbor)( coor, std::abs(pred) );
      float new_cost = reevaluateGap( pred_coor, cost, m_pred_map_1( pred_coor ) ) +cost;
      //m_cost_map_1( coor ) = new_cost;
      m_gap_ident( coor ) = m_gap_ident( pred_coor );
      return new_cost;
    }
    else
    {
      if( m_gap_ident( coor ) == -1 )
      {
        m_gap_ident( coor ) = m_gap_it;
        ++m_gap_it;
      }
      return m_cost_map_1( coor );
    }
  }


  VolumeI m_gap_range;
  double m_part_cost;
  int m_gap_length;

  int m_gap_it = 0;
  VolumeI &m_gap_ident;
};



class DjikstraWithVelocity : public DjikstraBase
{
public:
  DjikstraWithVelocity( const Volume& cost_input,
                        Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                        VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map,
                        const int idd, const float cost_cutoff, const utils::CoordinateF& mults,
                        const double cost_part, const int max_gap_length );

protected:
  void updateNeighborhood( const utils::Coordinate& coor, const float& cost ) override;

};

#endif // ADAPTED_DJIKSTRA_H__

