/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "graph_refinement.h"
#include "eval_root_order.h"

EdgeGenerator::EdgeGenerator( const Volume& rad_map, const Volume& cost_map, const utils::CoordinateD& dim_mults, std::vector<utils::Coordinate>& vertices )
: m_rad_map( rad_map ), m_cost_map( cost_map ), m_dim_mults( dim_mults ), m_pt_vec( vertices )
{}

void EdgeGenerator::operator()( const double& max_cost, const int& num_threads ){ findNeighbors( max_cost, num_threads ); }

void EdgeGenerator::findNeighbors( const double& max_cost, const int& num_threads )
{
  m_neighborhood = std::vector<Neighborhood>( m_pt_vec.size(), Neighborhood() );
  m_edges.clear();

  for( size_t t_it=0 ; t_it < num_threads ; ++t_it )
    m_threads.push_back( std::thread( &EdgeGenerator::findNeighborsThread, this, max_cost ) );
  for( size_t t_it=0 ; t_it < num_threads ; ++t_it )
    m_threads[t_it].join();

}


void EdgeGenerator::findNeighborsThread( const double& max_cost )
{
  int pt_it = m_pt_it.getIterator();
  while( pt_it < m_pt_vec.size() )
  {
    m_neighborhood.push_back( std::vector<int>() );
    findNeighborsPoint( m_pt_vec[pt_it], pt_it, max_cost );
    pt_it = m_pt_it.getIterator();
  }
}


void EdgeGenerator::findNeighborsPoint( const utils::Coordinate& pt, const int& cur_it, const double& max_cost )
{
  const utils::Coordinate& st_pt = m_pt_vec[cur_it];
  for( size_t pt_it=cur_it+1 ; pt_it < m_pt_vec.size() ; ++pt_it )
  {
    const utils::Coordinate& ed_pt = m_pt_vec[pt_it];
    utils::ScaledLine path( st_pt, ed_pt, m_dim_mults );
    path.normalize();
    std::cout << "DEB: " << st_pt << "->" << ed_pt << std::endl;
    double cost = evaluatePathCost( path );
    if( cost <= max_cost )
    {
      std::unique_lock<std::mutex> out_lock( m_out_mutex );
      m_edges.push_back( Edge( path.m, cost, cur_it, pt_it ) );
      m_neighborhood[cur_it].push_back( m_edges.size()-1 );
      m_neighborhood[pt_it].push_back( m_edges.size()-1 );
    }
  }
}


double EdgeGenerator::evaluatePathCost( const utils::Line& path )
{
  double cost = 0.0;
  for( size_t l_it=0 ; l_it < path.len ; ++l_it )
  {
    utils::Coordinate cur_pos = path( l_it ).toInt();
    cost += m_cost_map( cur_pos );
  }
  return cost;
}


extern "C" void rebuildGraph( void* graph_ptr, float* rad_map, float* cost_map,
                              int* shape, double* dim_mults, double max_cost, int num_threads )
{
  std::cout << "RebuildGraph" << std::endl;
  const utils::Coordinate c_shape( shape );
  const utils::CoordinateD c_dim_mults( dim_mults );
  std::cout << "shape=" << c_shape << std::endl << "mults=" << c_dim_mults << std::endl;
  const Volume v_rad_map( rad_map, c_shape ), v_cost_map( cost_map, c_shape );
  Graph* graph = reinterpret_cast<Graph*>( graph_ptr );

  std::vector<utils::Coordinate> vertices;
  graph->getPoints( vertices );
  std::cout << "Got vertices: " << vertices.size() << std::endl;
  EdgeGenerator edge_generator( v_rad_map, v_cost_map, c_dim_mults, vertices );
  edge_generator( max_cost, num_threads );
}


extern "C" void evalRootOrder( void* graph_ptr )
{
  std::cout << "EvalRootOrder" << std::endl;
  Graph* graph = reinterpret_cast<Graph*>( graph_ptr );
  Graph::BranchVector branches;
  graph->getBranches( branches );
  std::vector<utils::BranchValues> vals;
  utils::evaluateBranches( branches, vals );
}
