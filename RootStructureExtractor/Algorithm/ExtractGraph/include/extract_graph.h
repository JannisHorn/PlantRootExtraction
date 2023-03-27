/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef EXTRACT_GRAPH_H__
#define EXTRACT_GRAPH_H__

#include "root_graph.h"
#include "hash_table.h"
#include "volume.h"
#include "neighborhood.h"
#include "sphere_mask.h"

#define TYPE_NOT_COMPARABLE

class GraphExtractor
{
  //0. Add start point to list
  //1. get list of all nodes with int above threshold
  //2. for each node in list:
  //  2.1 if pred != 0 and pred !in_list
  //        add pred to list and create list_node for pred
  //      else fetch pred from list
  //  2.2 splice list_node(node) to pred list
public:
  struct Cutoff
  {
    Cutoff( const int& c_axis, const int& cut ) : axis(c_axis), coor( cut )
    {}

    void operator()( const utils::Coordinate& shape )
    {
      min_c = utils::Coordinate(0,0,0);
      max_c = shape;
      switch( axis )
      {
        case 0: min_c[0] = coor; break;
        case 1: max_c[0] = shape[0] -coor; break;
        case 2: min_c[1] = coor; break;
        case 3: max_c[1] = shape[1] -coor; break;
        case 4: min_c[2] = coor; break;
        case 5: max_c[2] = shape[2] -coor; break;
      }
    }

    size_t coor=0; int axis;
    utils::Coordinate min_c, max_c;
  };


  struct Path
  {
    size_t length;
    double avg_radius;
  };

  typedef utils::RootGraph Graph;

  GraphExtractor( const Volume& input, const Volume& cost_map_1, const Volume& cost_map_2,
                  const VolumeI& pred_map_1, const VolumeI& pred_map_2, Volume& out_arr );
  ~GraphExtractor() { delete m_neighbor; }

  Graph* extractGraph( const utils::Coordinate& start_pos,
                       const double& int_threshold,
                       const double& cost_cutoff );

  Graph* curveSkeletonization( const utils::Coordinate& start_pos,
                               Cutoff& z_cutoff,
                               const double& qp_min_dist,
                               const utils::CoordinateF& dim_mults,
                               const float& min_cmb, const int& dil_sum,
                               Graph* old_graph = nullptr,
                               const bool& seed_from_graph = false );

  std::string toXml();
  utils::xml::Element* nodeToXml( const Graph::NodePtr node );
  inline void deleteGraph() { delete m_graph; }

private:
  void findNodesByInt( const double& threshold );
  void buildGraph();
  void initVolumeFromGraph( const Graph::NodePtr& node, const double& dil_mult );
  utils::Coordinate getPredecessor( const utils::Coordinate& pos );
  Graph::NodePtr addGraphNode( const utils::Coordinate& pos, const bool connect=false, const float& rad=1.f );
  Graph::NodePtr addGraphNode( const utils::Coordinate& pos, const float& rad, const double& dil_sum, const size_t& branch_id );
  void fillRadius( const Graph::NodePtr& node, const utils::Coordinate& pos, const size_t& rad, const size_t& small_rad );
  void fillOutput( const utils::Coordinate& pos, const utils::Coordinate& sp_pos );
  void fillPosition( const Graph::NodePtr& node, const utils::Coordinate& pos, const utils::Coordinate& sp_pos );
  void getPathRadius( const utils::Coordinate& pos, Path& path );
  void getPathRadiusNode( const utils::Coordinate& pos, size_t& it, Path& path );


  const Volume &m_input, &m_cost_map_1, &m_cost_map_2;
  const VolumeI &m_pred_map_1, &m_pred_map_2;
  Volume& m_output;
  VolumeBase<void*> m_nodes_in_graph;
  Graph* m_graph;
  utils::Coordinate m_shape;
  int m_num_elems;

  double m_cost_cutoff, m_min_dist;
  double m_int_threshold;
  int m_id = 0;
  utils::CoordinateF m_mults;
  utils::NeighborhoodBase* m_neighbor;
  std::vector<Volume> m_spheres;
  size_t m_branch_iter = 0;
};

#endif // EXTRACT_GRAPH_H__

