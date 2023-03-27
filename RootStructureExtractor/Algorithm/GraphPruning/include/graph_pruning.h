/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef GRAPH_PRUNING_H__
#define GRAPH_PRUNING_H__

#include "root_graph.h"
#include "volume.h"

typedef utils::RootGraph Graph;

class RadiusPruning
{
public:
  RadiusPruning( utils::RootGraph* graph, const Volume& radius_map, Volume& output );
  void operator()();

private:
  int evaluatePosition( const utils::Coordinate& pos );

  utils::RootGraph* m_graph;
  const Volume& m_radius_map;
  Volume& m_output;
};


class Skeletonization
{
public:
  Skeletonization( const Volume& extracted_map, Volume& output );
  void operator()();

private:
  float evaluatePosition( const utils::Coordinate& pos );

  const Volume& m_extracted_map;
  Volume& m_skeleton;
};


class GrassFire
{
public:
  GrassFire( const Volume& extracted_map, Volume& output );
  Graph* operator()();

private:
  float evaluatePosition( const utils::Coordinate& pos );

  const Volume& m_extracted_map;
  Volume& m_skeleton;
};



class InterpolateGraph //Douglas Peucker Algorithm
{
public:
  InterpolateGraph( const Graph* graph );
  Graph* operator()( const double& max_diff );
private:
  void interpolate( Graph::Branch& branch );
  void interpolateSeg( Graph::Branch& branch,
                       const Graph::NodePtr& st_pt,
                       const Graph::NodePtr& ed_pt );

  const Graph* m_graph;
  double m_max_diff;
  std::vector<Graph::Branch> m_branches;
};

#endif // GRAPH_PRUNING_H__

