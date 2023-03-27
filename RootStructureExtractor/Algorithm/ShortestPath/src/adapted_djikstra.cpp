/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "adapted_djikstra.h"
#include <vector>

DjikstraBase::DjikstraBase( const Volume& input,
                                  Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                                  VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map, const int idd,
                                  const float cost_cutoff, const utils::CoordinateF& mults )
: m_input( input ),
  m_cost_map_1( n_1st_cost_map ), m_cost_map_2( n_2nd_cost_map ),
  m_pred_map_1( n_1st_pred_map ), m_pred_map_2( n_2nd_pred_map ),
  m_cost_cutoff( cost_cutoff )
{
  m_shape = m_input.getShape();
  m_num_elems = m_input.getSize();
  if( idd == 1 ) m_neighbor = new utils::NeighborhoodID1( m_shape, mults );
  else if( idd == 2 ) m_neighbor = new utils::NeighborhoodID2( m_shape, mults );
  else if( idd == 3 ) m_neighbor = new utils::NeighborhoodID3( m_shape, mults );
  m_mod_nodes.resize( m_neighbor->getMaxSize() ); // TODO
}

DjikstraBase::~DjikstraBase() { delete m_neighbor; }


void DjikstraBase::operator()( const utils::Coordinate& start_node )
{
  initShortestPath( start_node );
  shortestPath();
}

void DjikstraBase::initShortestPath( const utils::Coordinate& start_node )
{
  m_cost_map_1.fill( std::numeric_limits<float>::max() );
  m_cost_map_2.fill( std::numeric_limits<float>::max() );
  m_pred_map_1.fill( 0 );
  m_pred_map_2.fill( 0 );

  //m_unvisited_nodes.insert( 0, Node( start_node, 0 ) );
  m_unvisited_nodes.push( Node( start_node, 0, 0 ) );
  m_pred_map_1( start_node ) = -70;
  m_pred_map_2( start_node ) = -70;
  m_cost_map_1( start_node ) = 0;
  m_cost_map_2( start_node ) = 0;
}


void DjikstraBase::shortestPath()
{
  int run_it = 0, step_s = m_num_elems/1000;
  std::cout << "0" << "/" << m_num_elems;
  //while( !m_unvisited_nodes.isEmpty() )
  while( !m_unvisited_nodes.empty() )
  {
    Node curr_node( m_unvisited_nodes.top() );
    //float cost = m_unvisited_nodes.extractMin( curr_node );
    m_unvisited_nodes.pop();
    if( !nodeVisited( curr_node ) )
    {
      updateNode( curr_node.coor, curr_node.cost );
      ++run_it;
      if( (run_it % step_s) == 0 )
        std::cout << "\r" << run_it << "/" << m_num_elems;
    }
  }
  std::cout << "\r" << m_num_elems << "/" << m_num_elems << std::endl;
}


AdaptedDjikstra::AdaptedDjikstra( const Volume& input,
                                  Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                                  VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map, const int idd,
                                  const float cost_cutoff, const utils::CoordinateF& mults )
: DjikstraBase( input, n_1st_cost_map, n_2nd_cost_map,
                n_1st_pred_map, n_2nd_pred_map,
                idd, cost_cutoff, mults )
{
}


extern "C" int djikstraShortestPath( float* input, float* cost_map_1, float* cost_map_2,
                                     int* pred_map_1, int* pred_map_2,
                                     int x_dim, int y_dim, int z_dim, int* start_pos, int idd,
                                     float cost_cutoff, float* dim_mults )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim ), st_coor(start_pos);
  Volume v_input( input, shape ), v_cost_1( cost_map_1, shape ), v_cost_2( cost_map_2, shape );
  VolumeI v_pred_map_1( pred_map_1, shape ), v_pred_map_2( pred_map_2, shape );

  std::cout << "Input shape: " << shape << std::endl;
  std::cout << "Starting at " << st_coor << std::endl;
  std::cout << "Dim Mults: " << utils::CoordinateF( dim_mults ) << std::endl;
  AdaptedDjikstra djikstra( v_input, v_cost_1, v_cost_2, v_pred_map_1, v_pred_map_2, idd, cost_cutoff, utils::CoordinateF( dim_mults ) );
  djikstra( st_coor );
  return 0;
}




AdaptedDjikstraDirectionCost::AdaptedDjikstraDirectionCost( const Volume& input, const Volume& rad_map,
                                                            Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                                                            VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map, const int idd,
                                                            const float cost_cutoff, const utils::CoordinateF& mults,
                                                            const float dir_penalty_mult )
: DjikstraBase( input, n_1st_cost_map, n_2nd_cost_map,
                n_1st_pred_map, n_2nd_pred_map,
                idd, cost_cutoff, mults ),
  m_dir_penalty_mult( dir_penalty_mult ),
  m_rad_map( rad_map )
{
  m_rad_grads = Volume3D( input.getShape(), utils::CoordinateD( 0.0,0.0,0.0 ) );
  m_rad_map.getGradField( m_rad_grads );
}

extern "C" int djikstraShortestPathDirection( float* input, float* rad_map, float* cost_map_1, float* cost_map_2,
                                     int* pred_map_1, int* pred_map_2,
                                     int x_dim, int y_dim, int z_dim, int* start_pos, int idd,
                                     float cost_cutoff, float* dim_mults,
                                     float dir_pen )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim ), st_coor(start_pos);
  Volume v_input( input, shape ), v_rad( rad_map, shape ), v_cost_1( cost_map_1, shape ), v_cost_2( cost_map_2, shape );
  VolumeI v_pred_map_1( pred_map_1, shape ), v_pred_map_2( pred_map_2, shape );

  std::cout << "Input shape: " << shape << std::endl;
  std::cout << "Starting at " << st_coor << std::endl;
  std::cout << "Dim Mults: " << utils::CoordinateF( dim_mults ) << std::endl;
  std::cout << "Dir Penalty: " << dir_pen << std::endl;
  AdaptedDjikstraDirectionCost djikstra( v_input, v_rad, v_cost_1, v_cost_2, v_pred_map_1, v_pred_map_2, idd, cost_cutoff, utils::CoordinateF( dim_mults ), dir_pen );
  djikstra( st_coor );
  return 0;
}





DjikstraWithGapClosing::DjikstraWithGapClosing( const Volume& cost_input,
                                                Volume& n_1st_cost_map, Volume& n_2nd_cost_map,
                                                VolumeI& n_1st_pred_map, VolumeI& n_2nd_pred_map,
                                                VolumeI& n_gap_ident, const int idd,
                                                const float cost_cutoff, const utils::CoordinateF& mults,
                                                const double cost_part, const int max_gap_length )
: DjikstraBase( cost_input, n_1st_cost_map, n_2nd_cost_map,
                n_1st_pred_map, n_2nd_pred_map,
                idd, cost_cutoff, mults ),
  m_gap_range( cost_input.getShape(), 0 ),
  m_gap_ident( n_gap_ident ),
  m_gap_length( max_gap_length )
{
  m_part_cost = m_input.max() *cost_part;
  std::cout << "Min gap cost: " << m_part_cost << std::endl;
}



extern "C" int djikstraGapClosing( float* input, float* cost_map_1, float* cost_map_2,
                                   int* pred_map_1, int* pred_map_2, int* gap_map,
                                   int x_dim, int y_dim, int z_dim, int* start_pos, int idd,
                                   float cost_cutoff, float* dim_mults,
                                   double cost_per, int gap_length )
{
  //TODO djikstra once, search for min gaps missing for connection, fill again, repeat until full connectivity
  utils::Coordinate shape( x_dim, y_dim, z_dim ), st_coor(start_pos);
  Volume v_input( input, shape ), v_cost_1( cost_map_1, shape ), v_cost_2( cost_map_2, shape );
  VolumeI v_pred_map_1( pred_map_1, shape ), v_pred_map_2( pred_map_2, shape ), v_gap_map( gap_map, shape );

  std::cout << "Input shape: " << shape << std::endl;
  std::cout << "Starting at " << st_coor << std::endl;
  std::cout << "Dim Mults: " << utils::CoordinateF( dim_mults ) << std::endl;
  std::cout << "Gap: " << cost_per  << " length=" << gap_length << std::endl;
  DjikstraWithGapClosing djikstra( v_input, v_cost_1, v_cost_2, v_pred_map_1, v_pred_map_2, v_gap_map, idd, cost_cutoff, utils::CoordinateF( dim_mults ), cost_per, gap_length );
  djikstra( st_coor );
  return 0;
}
