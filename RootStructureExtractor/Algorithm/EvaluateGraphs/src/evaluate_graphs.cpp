/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "evaluate_graphs.h"

namespace utils
{

void correlatePointsAndGraph( const BranchPtList& g_list, const RootGraph& g_target, const double& mdist )
{
  for( size_t br_it=0 ; br_it < g_list.size() ; ++br_it )
  {

  }
}

bool

void checkBoundingBoxesBranch( const AlignedBoxD& br_box, const RootGraph::NodePtr& n_target )
{
  const RootGraph::NodeVector& childs = n_target->getChildren();
  for( size_t c_it=0 ; c_it < childs.size() ; ++c_it )
  {
    ++cur_it;
    box_target = AlignedBoxD( n_target->getVal().pos, childs[c_it]->getVal().pos );
    if( br_box.overlap( box_target ) ) target_its.push_back( cur_it );
    checkBoundingBoxesBranch( br_box, childs[c_it] );
  }
}

void checkBoundingBoxes( std::vector<int>& target_its, const std::vector<CoordinateD>& br_list, const RootGraph& g_target, const double& mdist )
{
  const CoordinateD& st_pt = br_list.front(), ed_pt = br_list.back();
  AlignedBoxD bounding_box( st_pt, ed_pt );
  bounding_box.enlarge( mdist );
  target_it = 0;
  foruit
}

}
