/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef EVAL_ROOT_ORDER_H_
#define EVAL_ROOT_ORDER_H_


#include "root_graph.h"
#include "dgf_to_branch_vals.h"
#include <math.h>
#include <vector>


namespace utils{

struct BranchValues{
  RootGraph::NodePtr root = nullptr;
  RootGraph::NodePtr leaf = nullptr;
  int root_it = 0;
  double radius = 0.0;
  double length = 0.0;
  double volume = 0.0;
  double angle_br = 0.0;
  double angle_hor = 0.0;
  double angle_vert = 0.0;

  void operator+=( const BranchValues& other )
  {
    radius += other.radius;
    length += other.length;
    volume += other.volume;
    angle_br += other.angle_br;
    angle_hor += other.angle_hor;
    angle_vert += other.angle_vert;
  }
  void operator-=( const BranchValues& other )
  {
    radius -= other.radius;
    length -= other.length;
    volume -= other.volume;
    angle_br -= other.angle_br;
    angle_hor -= other.angle_hor;
    angle_vert -= other.angle_vert;
  }

  void operator /=( const double& val )
  {
    radius /= val;
    length /= val;
    volume /= val;
  }

  void operator<( const BranchValues& other )
  {
    radius = ( radius < other.radius ) ? radius : other.radius;
    length = ( length < other.length ) ? length : other.length;
    volume = ( volume < other.volume ) ? volume : other.volume;
  }

  void operator>( const BranchValues& other )
  {
    radius = ( radius > other.radius ) ? radius : other.radius;
    length = ( length > other.length ) ? length : other.length;
    volume = ( volume > other.volume ) ? volume : other.volume;
  }

  void normalize( const BranchValues& range, const BranchValues& offset )
  {
    radius = ( radius-offset.radius ) /range.radius;
    length = ( length-offset.length ) /range.length;
    volume = ( volume-offset.volume ) /range.volume;
    angle_br /= length;
    angle_hor /= length;
    angle_vert /= length;
  }
};


typedef GridTree<BranchValues> BranchTree;

inline void evaluateBranches( const RootGraph::BranchVector& branches, std::vector<BranchValues>& out_vec )
{
  utils::Coordinate vert( 0,0,1 );

  out_vec.reserve( branches.size() );
  for( const RootGraph::Branch& branch : branches )
  {
    out_vec.push_back( BranchValues() );
    BranchValues& current_val = out_vec[out_vec.size()-1];
    RootGraph::NodePtr cur_node = branch.getStart(), last_node = branch.getRoot();
    current_val.root = last_node;
    current_val.root_it = branch.getRootIt();
    while( cur_node->rank() == 1 )
    {
      last_node = cur_node;
      cur_node = cur_node->getChild( 0 );
      double length = cur_node->getVal().pos.getDistance( last_node->getVal().pos );
      double rad = ( cur_node->getVal().rad +cur_node->getVal().rad ) /2;
      current_val.length += length;
      current_val.radius += rad *length;
      current_val.volume += length*M_PI*rad*rad;

      utils::Coordinate orientation = cur_node->getVal().pos -last_node->getVal().pos;
      current_val.angle_vert = vert.getAngle( orientation )*length;
      current_val.angle_hor = vert.getPlaneAngle( orientation )*length;
    }

    current_val.radius /= current_val.length;
    current_val.angle_hor /= current_val.length;
    current_val.angle_vert /= current_val.length;

    RootGraph::NodePtr br_in = branch.getRoot()->getPred();
    if( br_in != nullptr )
    {
      RootGraph::NodePtr br_out = branch.getRoot();
      utils::Coordinate or_in = br_out->getVal().pos -br_in->getVal().pos;
      utils::Coordinate or_out = br_out->getChild(0)->getVal().pos -br_out->getVal().pos;
      current_val.angle_br = or_in.getAngle( or_out );
    }
  }
}


inline void getBoundsBranchTreeNode( const BranchTree::NodePtr& ptr, BranchValues& lbound, BranchValues& ubound )
{
  const BranchValues& cur_val = ptr->getVal();
  lbound < cur_val;
  ubound > cur_val;
  for( size_t c_it=0 ; c_it < ptr->rank() ; ++c_it )
    getBoundsBranchTreeNode( ptr->getChild( c_it ), lbound, ubound );
}

inline void normalizeBranchTree( BranchTree& graph )
{
  BranchValues lbound, ubound;
  getBoundsBranchTreeNode( graph.getRoot(), lbound, ubound );
  BranchValues offset, range;
  offset += lbound;

}


inline size_t rootToValue( const std::vector<BranchValues>& br_vec, const size_t& it, const Graph::NodePtr& root )
{
  size_t out = 0;
  while( br_vec[out].root == root ) ++out;
  if( br_vec[out].root_it == it ) return out;
}


inline void buildBranchTreeNode( const RootGraph::NodePtr& node, const std::vector<BranchValues>& br_vec, BranchTree::NodePtr& out_node )
{
  RootGraph::NodePtr cur_node = node;
  while( cur_node->rank() == 1 ) cur_node = node->getChild( 0 );
  for( size_t r_it=0 ; r_it < cur_node->rank() ; ++r_it )
  {
    size_t node_it = rootToValue( br_vec, r_it, cur_node );
    BranchTree::NodePtr next_node = out_node->insert( new BranchTree::Node( br_vec[node_it] ) );
    buildBranchTreeNode( cur_node->getChild( r_it ), br_vec, next_node );
  }
}


inline void buildBranchTree( const RootGraph& graph, const std::vector<BranchValues>& br_vec, BranchTree& tree )
{
  size_t root_it = rootToValue( br_vec, 0, graph.getRoot() );
  BranchTree::NodePtr root = new BranchTree::Node( br_vec[root_it] );
  tree.setRoot( root );
  for( size_t r_it=0 ; r_it < graph.getRoot()->rank() ; ++r_it )
    buildBranchTreeNode( graph.getRoot(), br_vec, root );
}


inline void evalFromLeafTo( std::vector<BranchValues>& out_vec, const std::vector<BranchTree::NodePtr>& leafs,
                            const Graph::NodePtr& leaf, const Graph::NodePtr& root )
{
  out_vec.push_back( BranchValues() );
  BranchValues& cur_val = out_vec[out_vec.size()-1];
  BranchTree::NodePtr cur_node;
  int l_it=0;
  while( leafs[l_it]->getVal().leaf != leaf ) ++l_it;
  cur_node = leafs[l_it];
  cur_val += cur_node->getVal();
  while( cur_node->getVal().root != root )
  {
    cur_node = cur_node->getPred();
    cur_val += cur_node->getVal();
  }
}


}

#endif // EVAL_ROOT_ORDER_H_
