/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef DGF_TO_BRANCH_VALS_H__
#define DGF_TO_BRANCH_VALS_H__

#include <fstream>
#include <string>
#include "utils.h"
#include "root_graph.h"
#include "eval_root_order.h"

namespace utils{

inline void getPoints( std::ifstream& stream, const utils::Coordinate& size, std::vector<CoordinateD>& out_vec )
{
  std::string line;
  while( std::getline( stream, line ) )
  {
    std::istringstream iss( line );
    std::string s = iss.str();
    if( s.find( "#" ) != std::string::npos ) return;
    std::vector<double> vals;
    vals.reserve(3);
    double fac;
    size_t it = 0, start = 0, end = 0;
    while (end != std::string::npos)
    {
      while( s[start] == (' ') && start != std::string::npos ) ++start;
      end = s.find(" ", start);
      if( end == std::string::npos ) break;
      std::string sub = s.substr(start, end - start);
      start = end + 1;
      vals.push_back( std::stod( sub ) );
    }
    out_vec.push_back( utils::CoordinateD( vals ).scalarMult( size ) );
  }
}


template<int>
struct LineArgument {};

template<> struct LineArgument<0>
{ LineArgument( const std::vector<std::string>& subs ){ st_node=std::stoi( subs[0] ); } int st_node; };
template<> struct LineArgument<1> : LineArgument <0>
{ LineArgument( const std::vector<std::string>& subs ) : LineArgument<0>( subs ) { e_node=std::stoi( subs[1] ); } int e_node; };
template<> struct LineArgument<2> : LineArgument <1>
{ LineArgument( const std::vector<std::string>& subs ) : LineArgument<1>( subs ) { order=std::stoi( subs[2] ); } int order; };
template<> struct LineArgument<3> : LineArgument <2>
{ LineArgument( const std::vector<std::string>& subs ) : LineArgument<2>( subs ) { br_id=std::stoi( subs[3] ); } int br_id; };
template<> struct LineArgument<4> : LineArgument <3>
{ LineArgument( const std::vector<std::string>& subs ) : LineArgument<3>( subs ) { radius=std::stod( subs[6] ); } double radius; };

inline LineArgument<4> lineToNodeArgs( const std::string& line )
{
  std::vector<std::string> substrings;
  size_t it = 0, start = 0, end = 0;
  while (end != std::string::npos)
  {
    while( line[start] == (' ') && start != std::string::npos ) ++start;
    end = line.find(" ", start);
    if( end == std::string::npos ) break;
    substrings.push_back( line.substr(start, end - start) );
    start = end + 1;
  }
  return LineArgument<4>( substrings );
}


inline void getSegments( std::ifstream& stream, std::vector<LineArgument<4>>& out_vec )
{
  std::string line;
  while( std::getline( stream, line ) )
  {
    std::istringstream iss( line );
    std::string s = iss.str();
    if( s.find( "#" ) != std::string::npos ) return;
    out_vec.push_back( lineToNodeArgs( s ) );
  }
}


inline void buildGraph( const std::vector<CoordinateD>& points,
                 const std::vector<LineArgument<4>> args, RootGraph& graph )
{
  std::vector<RootGraph::NodePtr> nodes;
  nodes.reserve( points.size() );
  RootGraph::NodePtr root = new RootGraph::Node( points[0].toInt(), args[0].radius, args[0].br_id );
  nodes.push_back( root );
  for( size_t n_it=1 ; n_it < points.size() ; ++n_it )
  {
    nodes.push_back( new RootGraph::Node( points[n_it].toInt(), args[n_it-1].radius, args[n_it-1].br_id ) );
    nodes[args[n_it-1].st_node]->insert( nodes[n_it] );
  }
  graph.repairPreds();
}


inline void dgfToRootGraph( const std::string& fname, const utils::Coordinate size, RootGraph& graph )
{
  std::ifstream fss;
  fss.open( fname );
  std::string s;
  std::getline( fss, s );
  std::getline( fss, s );
  std::getline( fss, s );

  std::vector<CoordinateD> pts;
  getPoints( fss, size, pts );
  std::getline( fss, s );
  std::getline( fss, s );
  std::getline( fss, s );

  std::vector<LineArgument<4>> args;
  getSegments( fss, args );
  buildGraph( pts, args, graph );
}


}

#endif // DGF_TO_BRANCH_VALS_H__
