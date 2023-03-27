/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "graph_pruning.h"

RadiusPruning::RadiusPruning( utils::RootGraph* graph, const Volume& radius_map, Volume& output )
  : m_graph( graph ), m_radius_map( radius_map ), m_output( output ) {};


//int RadiusPruning::evaluatePosition( const utils::Coordinate& pos )
//{
//
//}


void RadiusPruning::operator()()
{
  utils::RootGraph::NodeVector leafs;
  m_graph->getLeafs( leafs );

  utils::Coordinate shape = m_radius_map.getShape();
  for( size_t z=0; z < shape[2] ; ++z )
    for( size_t y=0; y < shape[1] ; ++y )
      for( size_t x=0; x < shape[0] ; ++x )
      {

      }
}




Skeletonization::Skeletonization( const Volume& extracted_map, Volume& output )
  : m_extracted_map( extracted_map ), m_skeleton( output ) {}


void Skeletonization::operator()( )
{
  utils::Coordinate shape = m_extracted_map.getShape();

  float cutoff = 21;
  for( size_t z=1; z < shape[2]-1 ; ++z )
    for( size_t y=1; y < shape[1]-1 ; ++y )
      for( size_t x=1; x < shape[0]-1 ; ++x )
      {
        float val = evaluatePosition( utils::Coordinate( x,y,z ) );
        m_skeleton( x,y,z ) = val;
      }
}


float Skeletonization::evaluatePosition( const utils::Coordinate& pos )
{
  const float& val = m_extracted_map( pos );
  float sum = 0;
  const int& x=pos[0]; const int& y=pos[1]; const int& z=pos[2];
  //for( int x_it=-1 ; x_it < 2 ; ++x_it )
  //  for( int y_it=-1 ; y_it < 2 ; ++y_it )
  //    for( int z_it=-1 ; z_it < 2 ; ++z_it )
  //    {
  //      if( m_extracted_map( x+x_it, y+y_it, z+z_it ) < val ) sum+=1.0;
  //      else if( m_extracted_map( x+x_it, y+y_it, z+z_it ) == val ) sum+=0.5;
  //    }
  if( m_extracted_map( x+1, y, z ) < val ) sum+=1;
  if( m_extracted_map( x+1, y, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x+1, y, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x+1, y+1, z ) < val ) sum+=1;
  if( m_extracted_map( x+1, y+1, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x+1, y+1, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x+1, y-1, z ) < val ) sum+=1;
  if( m_extracted_map( x+1, y-1, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x+1, y-1, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x-1, y, z ) < val ) sum+=1;
  if( m_extracted_map( x-1, y+1, z ) < val ) sum+=1;
  if( m_extracted_map( x-1, y-1, z ) < val ) sum+=1;
  if( m_extracted_map( x-1, y, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x-1, y, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x-1, y+1, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x-1, y+1, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x-1, y-1, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x-1, y-1, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x, y+1, z ) < val ) sum+=1;
  if( m_extracted_map( x, y+1, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x, y+1, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x, y-1, z ) < val ) sum+=1;
  if( m_extracted_map( x, y-1, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x, y-1, z-1 ) < val ) sum+=1;
  if( m_extracted_map( x, y, z+1 ) < val ) sum+=1;
  if( m_extracted_map( x, y, z-1 ) < val ) sum+=1;
  return sum;
}

extern "C" void skeletonization( float* radius_arr, float* output, int x_dim, int y_dim, int z_dim )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim );
  Volume v_rad( radius_arr, shape ), v_out( output, shape );

  std::cout << "Max radius: " << v_rad.max() << std::endl;
  Skeletonization skel( v_rad, v_out );
  skel();
}



GrassFire::GrassFire( const Volume& extracted_map, Volume& output )
  : m_extracted_map( extracted_map ), m_skeleton( output ) {}


Graph* GrassFire::operator()()
{
  utils::Coordinate shape = m_extracted_map.getShape();
  Graph* graph = new Graph();
  m_skeleton.copyFrom( m_extracted_map );

  float cutoff = 13;
  bool finished = false;
  while( !finished )
  {
    std::cout << "Iter " << std::endl;
    finished = true;
    for( size_t z=1; z < shape[2]-1 ; ++z )
      for( size_t y=1; y < shape[1]-1 ; ++y )
        for( size_t x=1; x < shape[0]-1 ; ++x )
        {
          if( m_skeleton(x,y,z) > 0 )
            if( evaluatePosition( utils::Coordinate( x,y,z ) ) < cutoff )
            {
              finished = false;
              m_skeleton( x,y,z ) = 0;
            }
            else
              m_skeleton( x,y,z ) = 1;
        }
  }

  return graph;
}


float  GrassFire::evaluatePosition( const utils::Coordinate& pos )
{
  float val = m_extracted_map( pos );
  float sum = 0;
  const int& x=pos[0]; const int& y=pos[1]; const int& z=pos[2];
  if( m_extracted_map( x+1, y, z ) == 0 ) sum+=1;
  if( m_extracted_map( x+1, y+1, z ) == 0 ) sum+=1;
  if( m_extracted_map( x+1, y-1, z ) == 0 ) sum+=1;
  if( m_extracted_map( x+1, y, z+1 ) == 0 ) sum+=1;
  if( m_extracted_map( x+1, y, z-1 ) == 0 ) sum+=1;
  if( m_extracted_map( x-1, y, z ) == 0 ) sum+=1;
  if( m_extracted_map( x-1, y+1, z ) == 0 ) sum+=1;
  if( m_extracted_map( x-1, y-1, z ) == 0 ) sum+=1;
  if( m_extracted_map( x-1, y, z+1 ) == 0 ) sum+=1;
  if( m_extracted_map( x-1, y, z-1 ) == 0 ) sum+=1;
  if( m_extracted_map( x, y+1, z ) == 0 ) sum+=1;
  if( m_extracted_map( x, y+1, z+1 ) == 0 ) sum+=1;
  if( m_extracted_map( x, y+1, z-1 ) == 0 ) sum+=1;
  if( m_extracted_map( x, y-1, z ) == 0 ) sum+=1;
  if( m_extracted_map( x, y-1, z+1 ) == 0 ) sum+=1;
  if( m_extracted_map( x, y-1, z-1 ) == 0 ) sum+=1;
  if( m_extracted_map( x, y, z+1 ) == 0 ) sum+=1;
  if( m_extracted_map( x, y, z-1 ) == 0 ) sum+=1;
  return sum;
}


extern "C" void grassFire( float* radius_arr, float* output, int x_dim, int y_dim, int z_dim )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim );
  Volume v_rad( radius_arr, shape ), v_out( output, shape );

  std::cout << v_rad.max() << std::endl;
  GrassFire skel( v_rad, v_out );
  skel();
}



InterpolateGraph::InterpolateGraph( const Graph* graph ) : m_graph( graph ) {}

Graph* InterpolateGraph::operator()( const double& max_diff )
{
  Graph* out_graph = new Graph( *m_graph );
  out_graph->insert( *( m_graph->getRoot() ) );

  Graph::BranchVector branches;
  out_graph->getBranches( branches );
  m_max_diff = std::pow( max_diff, 2 );
  std::cout << "Got " << branches.size() << " Branches" << std::endl;
  for( size_t it=0; it < branches.size() ; ++it )
    interpolate( branches[it] );

  delete m_graph;
  return out_graph;
}

void InterpolateGraph::interpolate( Graph::Branch& branch )
{
  Graph::NodePtr st_pt = branch.getRoot(), ed_pt = branch.getTail();
  interpolateSeg( branch, st_pt, ed_pt );
}

void InterpolateGraph::interpolateSeg( Graph::Branch& branch,
                                       const Graph::NodePtr& st_pt,
                                       const Graph::NodePtr& ed_pt )
{
  if( ed_pt->getPred() == st_pt )
    return;
  utils::Line line( st_pt->getVal().pos, ed_pt->getVal().pos );
  Graph::NodePtr max_pos;
  double max_diff = 0.0;
  Graph::NodePtr start_pt;
  if( st_pt == branch.getRoot() )
    start_pt = branch.getStart();
  else
    start_pt = st_pt->getChilds()[0];
  branch.setIter( start_pt );

  for( Graph::NodePtr curr_iter = branch.getIter();
       curr_iter != ed_pt;
       curr_iter = branch.next() )
  {
    double diff = line.distSqrd( curr_iter->getVal().pos );
    if( diff > max_diff )
    {
      max_diff = diff;
      max_pos = curr_iter;
    }
  }
  if( max_diff < m_max_diff )
    branch.deleteSegment( start_pt, ed_pt );
  else
  {
    interpolateSeg( branch, st_pt, max_pos );
    interpolateSeg( branch, max_pos, ed_pt );
  }
}

extern "C" Graph* interpolateGraph( void* graph, double max_diff, const char* path )
{
  InterpolateGraph interpolator( reinterpret_cast<Graph*>( graph ) );
  Graph* int_graph = interpolator( max_diff );
  std::string tpath( path );
  //if( tpath == "" )
  //  tpath = "interpolate.xml";
  //int_graph->saveToFile(tpath);
  return  int_graph;
}


extern "C" void maskVolumeByGraph( float* output, int* shape_ptr, float* dim_facs_ptr,
                                    void* graph_ptr, float value, double rad_rate )
{
  std::cout << "Entering" << std::endl;
  utils::Coordinate shape( shape_ptr );
  utils::CoordinateF dim_facs( dim_facs_ptr );
  Volume v_output( output, shape );
  std::cout << "Shape: " << shape << ", DimFacs: " << dim_facs << std::endl;

  Graph* graph = reinterpret_cast<Graph*>( graph_ptr );
  std::cout << "Enter Graph" << std::endl;
  graph->fillVolume( v_output, dim_facs, value, rad_rate );
}



double getBranchLength( Graph::Branch& branch )
{
  if( branch.size() <= 1 ) return 1.0;
  utils::Coordinate last_pos = branch.getRoot()->getVal().pos;
  double length = 0.0;
  Graph::NodePtr cur_node = branch.getStart();
  branch.setIter( cur_node );

  for( Graph::NodePtr curr_iter = branch.getIter();
       curr_iter != branch.getTail();
       curr_iter = branch.next() )
  {
    utils::Coordinate cur_pos = curr_iter->getVal().pos;
    length += cur_pos.getSqrdDistance( last_pos );
    last_pos = cur_pos;
  }
  return length;
}

extern "C" void pruneShortBranches( void* graph_ptr, double min_length )
{
  std::cout << "Pruning short branches: " << min_length << std::endl;
  Graph* input_graph = static_cast<Graph*>( graph_ptr );
  const double sqrd_min_l = min_length*min_length;
  bool cont = true;
  while( cont )
  {
    cont = false;
    Graph::BranchVector branches;
    input_graph->getBranches( branches ); // Dont generate new vector every time -> update function
    for( int b_it=branches.size()-1 ; b_it >= 0 ; --b_it )
    {
      Graph::Branch& branch = branches[b_it];
      if( branch.getTail()->rank() == 0 )
      {
        double sqrd_length = getBranchLength( branch );
        if( sqrd_length < sqrd_min_l )
        {
          branch.deleteLeafBranch();
          cont = true;
          std::cout << "Deleting branch of sqrd length: " << sqrd_length << std::endl;
        }
      }
    }
  }
}



double getBranchRadius( Graph::Branch& branch )
{
  if( branch.size() <= 1 ) return 1.0;
  utils::Coordinate last_pos = branch.getRoot()->getVal().pos;
  double radius = 0.0;
  double full_l = 0.0;
  Graph::NodePtr cur_node = branch.getStart();
  branch.setIter( cur_node );

  for( Graph::NodePtr curr_iter = branch.getIter();
       curr_iter != branch.getTail();
       curr_iter = branch.next() )
  {
    utils::Coordinate cur_pos = curr_iter->getVal().pos;
    double length = cur_pos.getDistance( last_pos );
    last_pos = cur_pos;
    radius += curr_iter->getVal().rad *length;
    full_l += length;
  }
  return radius /full_l;
}

extern "C" void pruneThinBranches( void* graph_ptr, double min_radius )
{
  std::cout << "Pruning thin branches: " << min_radius << std::endl;
  Graph* input_graph = static_cast<Graph*>( graph_ptr );
  bool cont = true;
  while( cont )
  {
    cont = false;
    Graph::BranchVector branches;
    input_graph->getBranches( branches ); // Dont generate new vector every time -> update function
    for( int b_it=branches.size()-1 ; b_it >= 0 ; --b_it )
    {
      Graph::Branch& branch = branches[b_it];
      if( branch.getTail()->rank() == 0 )
      {
        double rad = getBranchRadius( branch );
        if( rad < min_radius )
        {
          branch.deleteLeafBranch();
          cont = true;
          std::cout << "Deleting branch of acc radius: " << rad << std::endl;
        }
      }
    }
  }
}



extern "C" void* genVoid()
{
  int* val = new int(52);
  return reinterpret_cast<void*>(val);
}

extern "C" void catchVoid( void* val_ptr )
{
  int* val = reinterpret_cast<int*>( val_ptr );
  std::cout << "Got: " << *val << std::endl;
  delete val;
}
