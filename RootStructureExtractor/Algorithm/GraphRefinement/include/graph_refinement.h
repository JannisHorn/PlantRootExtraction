/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef GRAPH_REFINEMENT_H__
#define GRAPH_REFINEMENT_H__

#include "root_graph.h"
#include <mutex>
#include <thread>



typedef utils::RootGraph Graph;

void findMainBranch( Graph* input_graph );


struct Edge
{
  Edge( const utils::CoordinateD& dir, const double& cst, const int& s_it, const int& e_it )
    : direction(dir), cost(cst), st_it(s_it), ed_it(e_it) {}

  utils::CoordinateD direction;
  double cost, sqrd_len;
  int st_it, ed_it;
};

typedef std::vector<Edge> Edges;
typedef std::vector<int> Neighborhood;

class EdgeGenerator
{
public:

  struct Iterator
  {
  public:
    int getIterator()
    {
      std::unique_lock<std::mutex> lock( m_mutex );
      int return_val = pt_it;
      ++pt_it;
      return return_val;
    }
  private:
    std::mutex m_mutex;
    int pt_it = 0;
  };

  EdgeGenerator( const Volume& rad_map, const Volume& cost_map,
                 const utils::CoordinateD& dim_mults, std::vector<utils::Coordinate>& vertices );
  void operator()( const double& max_cost, const int& num_threads );

protected:
  void findNeighbors( const double& max_cost, const int& num_threads );
  void findNeighborsThread( const double& max_cost );
  void findNeighborsPoint( const utils::Coordinate& pt, const int& cur_it, const double& max_cost );
  double evaluatePathCost( const utils::Line& path );

  const Volume &m_rad_map;
  const Volume &m_cost_map;
  const utils::CoordinateD &m_dim_mults;
  std::vector<utils::Coordinate> &m_pt_vec;
  std::vector<Neighborhood> m_neighborhood;
  Edges m_edges;
  std::vector<std::thread> m_threads;
  Iterator m_pt_it;
  std::mutex m_out_mutex;
};

#endif // GRAPH_REFINEMENT_H__
