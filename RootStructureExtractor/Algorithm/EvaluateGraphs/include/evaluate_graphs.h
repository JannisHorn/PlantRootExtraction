/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef EVAL_GRAPHS_H_
#define EVAL_GRAPHS_H_

#include <vector>
#include "root_graph.h"

namespace utils
{

typedef std::vector<std::vector<CoordinateD>> BranchPtList;

/**
 * Given a graph in dense point form and a Rootgraph, return correspondence list
 *
 * @param g_list Input graph in dense point form
 * @param g_target Input target graph in graph form
 * @param mdist Maximum distance for point correlations
 */
void correlatePointsAndGraph( const BranchPtList& g_list, const RootGraph& g_target, const double& mdist );


/**
 * Compare points to branch bounding box of target graph
 *
 * @param br_list Branch as point list
 * @param g_target Target graph
 * @param mdist Maximum distance to allow correspondence
 * @return Sorted list of possible branches
 */
void checkBoundingBoxes( std::vector<int>& target_its, const std::vector<CoordinateD>& br_list, const RootGraph& g_target, const double& mdist );

}
#endif EVAL_GRAPHS_H_
