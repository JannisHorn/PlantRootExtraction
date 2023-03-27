/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include "extract_graph.h"

inline std::ostream& operator<<( std::ostream& _ostr, const VolumeBase<void*>& _obj )
{
  return _ostr << _obj.toString();
}


GraphExtractor::GraphExtractor( const Volume& input, const Volume& cost_map_1, const Volume& cost_map_2,
                                const VolumeI& pred_map_1, const VolumeI& pred_map_2, Volume& output )
                              : m_input( input ),
                                m_cost_map_1( cost_map_1 ), m_cost_map_2( cost_map_2 ),
                                m_pred_map_1( pred_map_1 ), m_pred_map_2( pred_map_2 ),
                                m_output( output ),
                                m_nodes_in_graph( VolumeBase<void*>( input.getShape(), nullptr ) )
{
  m_shape = m_input.getShape();
  m_num_elems = m_shape[0] *m_shape[1] *m_shape[2];
  m_neighbor = new utils::NeighborhoodID3( m_shape, m_mults );
}

GraphExtractor::Graph* GraphExtractor::extractGraph( const utils::Coordinate& start_pos,
                                                     const double& int_threshold,
                                                     const double& cost_cutoff )
{
  std::cout << "Enter" << std::endl;
  GraphExtractor::Graph::NodePtr root = new GraphExtractor::Graph::Node( start_pos );
  m_graph = new Graph( root );
  std::cout << "Got new Graph" << std::endl;
  m_nodes_in_graph( start_pos ) = root;
  m_output( start_pos ) = 1.0;
  m_cost_cutoff = cost_cutoff;
  m_int_threshold = int_threshold;
  size_t run_it = 0, step_s = m_num_elems/100;
  std::cout << "Initialized" << std::endl;
  for( size_t z=0; z < m_shape[2] ; ++z )
    for( size_t y=0; y < m_shape[1] ; ++y )
      for( size_t x=0; x < m_shape[0] ; ++x )
      {
        addGraphNode( utils::Coordinate( x,y,z ) );
        ++run_it;
        if( run_it % step_s == 0 )
          std::cout << run_it << "/" << m_num_elems << "\r";
      }
  std::cout << m_num_elems << "/" << m_num_elems << std::endl;
  return m_graph;
}


utils::Coordinate GraphExtractor::getPredecessor( const utils::Coordinate& pos )
{
  const int pred_code = m_pred_map_1( pos );
  switch( pred_code )
  {
    case 32: return pos.addElem( 1,0 );
    case 16: return pos.addElem( -1,0 );
    case 8: return pos.addElem( 1,1 );
    case 4: return pos.addElem( -1,1 );
    case 2: return pos.addElem( 1,2 );
    case 1: return pos.addElem( -1,2 );
    default: return pos;
  }
}

GraphExtractor::Graph::NodePtr GraphExtractor::addGraphNode( const utils::Coordinate& pos, bool connect, const float& rad )
{
  if( m_nodes_in_graph( pos ) != nullptr )
    return reinterpret_cast<Graph::NodePtr>( m_nodes_in_graph( pos ) );
  else{
    if( m_cost_map_1( pos ) < m_cost_cutoff && ( m_input( pos ) >= m_int_threshold || connect ) )
    {
      utils::Coordinate pred_pos = m_neighbor->operator()( pos, m_pred_map_1( pos ) );
      if( pos != pred_pos )
      {
        m_output( pos ) = 1.0;
        GraphExtractor::Graph::NodePtr pred = addGraphNode( pred_pos, true );
        GraphExtractor::Graph::NodePtr this_node = pred->insert( pos, rad, 0 );
        m_nodes_in_graph( pos ) = reinterpret_cast<void*>( this_node );
        return this_node;
      }
    }
  }
  return nullptr;
}




GraphExtractor::Graph* GraphExtractor::curveSkeletonization( const utils::Coordinate& start_pos,
                                                             Cutoff& z_cutoff,
                                                             const double& qp_min_dist,
                                                             const utils::CoordinateF& dim_mults,
                                                             const float& min_cmb, const int& dil_sum,
                                                             Graph* old_graph,
                                                             const bool& seed_from_graph )
{
  //std::cout << "___CURVE___" << std::endl;
  m_min_dist = qp_min_dist *qp_min_dist;
  double dil_mult = 1+ (dil_sum/100);
  float rad_max = std::ceil( m_cost_map_1.max() *dil_mult +1 );
  m_spheres.reserve( rad_max +1 );
  for( size_t rad=0; rad <= rad_max ; ++rad )
  {
    Volume sphere;
    sphereMask( sphere, rad, dim_mults );
    m_spheres.push_back( std::move( sphere ) );
  }
  if( old_graph == nullptr || seed_from_graph )
  {
    GraphExtractor::Graph::NodePtr root = new GraphExtractor::Graph::Node( start_pos );
    m_graph = new Graph( root );
    m_nodes_in_graph( start_pos ) = root;
    m_output( start_pos ) = 1.0;
  }
  else
  {
    m_graph = new Graph( *old_graph );
    initVolumeFromGraph( m_graph->getRoot(), dil_mult );
  }
  size_t ct = 0;
  std::cout << "Root: " << m_graph->getRoot()->getVal().pos << std::endl;

  z_cutoff( m_shape );
  const utils::Coordinate& mins = z_cutoff.min_c, &maxs = z_cutoff.max_c;
  std::cout << mins << " -> " << maxs << std::endl;
  std::vector<utils::Coordinate> quench_points;
  std::vector<double> quench_sqrd_dists;
  if( seed_from_graph && old_graph != nullptr )
  {
    std::cout << "Seed from old graph" << std::endl;
    Graph::NodeVector leafs;
    old_graph->getLeafs( leafs );
    for( const Graph::NodePtr& node : leafs )
    {
      const utils::Coordinate& pos = node->getVal().pos;
      quench_points.push_back( pos );
      Path qp_path;
      getPathRadius( pos, qp_path );
      quench_sqrd_dists.push_back( qp_path.avg_radius +qp_path.length +m_shape.z()-pos.z() );
    }
  }
  else
  {
    for( size_t z=mins[2]; z < maxs[2] ; ++z )
      for( size_t y=mins[1]; y < maxs[1] ; ++y )
        for( size_t x=mins[0]; x < maxs[0] ; ++x )
        {
          if( m_input(x,y,z) >= min_cmb )
          {
            double sqrd_dist = start_pos.getSqrdDistance( utils::Coordinate(x,y,z) );
            if( sqrd_dist > m_min_dist )
            {
              quench_points.push_back( utils::Coordinate(x,y,z) );
              quench_sqrd_dists.push_back( sqrd_dist );
            }
          }
        }
  }
  std::cout << "qp " << quench_points.size() << ", qp_d " << quench_sqrd_dists.size() << std::endl;
  float max_val = -1;
  utils::Coordinate max_pos;
  while( true )
  {
    for( size_t qp_it=0; qp_it < quench_points.size() ; ++qp_it )
    {
      if( m_output( quench_points[qp_it] ) != 0 || m_pred_map_1(quench_points[qp_it]) == 0 )
        quench_sqrd_dists[qp_it] = -1;
      else if( quench_sqrd_dists[qp_it] > max_val )
      {
        max_val = quench_sqrd_dists[qp_it];
        max_pos = quench_points[qp_it];
        //TODO remember second longest when dist first ~= second
      }
    }
    if( max_val == -1 ) break;
    max_val = -1;
    std::cout << "Branch " << ++ct << ": " << max_pos << " Rad: " << m_cost_map_1(max_pos) << std::endl;
    Graph::NodePtr end_node = addGraphNode( max_pos, m_cost_map_1( max_pos ), dil_mult, ++m_branch_iter );
  }
  return m_graph;
}


GraphExtractor::Graph::NodePtr GraphExtractor::addGraphNode( const utils::Coordinate& pos, const float& rad, const double& dil_sum, const size_t& branch_id )
{
  //std::cout << "NewNode: " << pos << std::endl;
  if( m_nodes_in_graph( pos ) != nullptr )
    return reinterpret_cast<Graph::NodePtr>( m_nodes_in_graph( pos ) );
  else{
    utils::Coordinate pred_pos = m_neighbor->operator()( pos, m_pred_map_1( pos ) );
    if( pos != pred_pos )
    {
      m_output( pos ) = 1.0;
      GraphExtractor::Graph::NodePtr pred = addGraphNode( pred_pos, m_cost_map_1( pred_pos ), dil_sum, branch_id );
      //std::cout << pred << std::endl;
      GraphExtractor::Graph::NodePtr this_node = pred->insert( pos, rad, branch_id );
      //std::cout << "Connected" << std::endl;
      fillRadius( this_node, pos, std::ceil( rad*dil_sum ), rad ); // TODO needs enhancement -> guided dilation?
      m_nodes_in_graph( pos ) = reinterpret_cast<void*>( this_node );
      return this_node;
    }
  }
  return nullptr;
}


void GraphExtractor::fillRadius( const Graph::NodePtr& node, const utils::Coordinate& pos,
                                 const size_t& radius, const size_t& small_radius )
{
  int min_it = std::min( pos.min() -int(radius), (m_output.getShape()-(pos+radius+1)).min() );
  size_t small_rad = small_radius, rad = radius;;
  if( min_it < 0 )
  {
    rad = rad +min_it;
    small_rad = std::min( rad, small_radius +min_it );
    //std::cout << min_it << ": " << rad <<  std::endl;
  }
  {
    //std::cout << "Pos: " << pos << ", Rad: " << rad << ", " << m_spheres.size() << std::endl;
    if( min_it < 0 )
      rad = radius +min_it;
    size_t diameter = rad *2 +1;
    Volume& sphere = m_spheres[rad];
    for( size_t z=0; z <= rad ; ++z )
      for( size_t y=0; y <= rad ; ++y )
        for( size_t x=0; x <= rad ; ++x )
        {
          if( sphere( x,y,z ) > 0.0 )
          {
            utils::Coordinate anchor = utils::Coordinate( pos[0]-rad,pos[1]-rad,pos[2]-rad );
            const size_t c_x = diameter -x -1;
            const size_t c_y = diameter -y -1;
            const size_t c_z = diameter -z -1;
            //std::cout << "rad:" << rad << ": " << anchor << "->" << x << "," << y << "," << z << " ; ";
            fillOutput( anchor, utils::Coordinate( x, y, z ) );
            fillOutput( anchor, utils::Coordinate( x, y, c_z ) );
            fillOutput( anchor, utils::Coordinate( x, c_y, z ) );
            fillOutput( anchor, utils::Coordinate( x, c_y, c_z ) );
            fillOutput( anchor, utils::Coordinate( c_x, y, z ) );
            fillOutput( anchor, utils::Coordinate( c_x, y, c_z ) );
            fillOutput( anchor, utils::Coordinate( c_x, c_y, z ) );
            fillOutput( anchor, utils::Coordinate( c_x, c_y, c_z ) );
          }
        }
  }
  {
    size_t diameter = small_rad*2+1;
    Volume& sphere = m_spheres[small_rad];
    for( size_t z=0; z <= small_rad ; ++z )
      for( size_t y=0; y <= small_rad ; ++y )
        for( size_t x=0; x <= small_rad ; ++x )
        {
          if( sphere( x,y,z ) > 0.0 )
          {
            utils::Coordinate anchor = utils::Coordinate( pos[0]-small_rad,pos[1]-small_rad,pos[2]-small_rad );
            const size_t c_x = diameter -x -1;
            const size_t c_y = diameter -y -1;
            const size_t c_z = diameter -z -1;
            fillPosition( node, anchor, utils::Coordinate( x, y, z ) );
            fillPosition( node, anchor, utils::Coordinate( x, y, c_z ) );
            fillPosition( node, anchor, utils::Coordinate( x, c_y, z ) );
            fillPosition( node, anchor, utils::Coordinate( x, c_y, c_z ) );
            fillPosition( node, anchor, utils::Coordinate( c_x, y, z ) );
            fillPosition( node, anchor, utils::Coordinate( c_x, y, c_z ) );
            fillPosition( node, anchor, utils::Coordinate( c_x, c_y, z ) );
            fillPosition( node, anchor, utils::Coordinate( c_x, c_y, c_z ) );
          }
        }
  }
}

void GraphExtractor::fillOutput( const utils::Coordinate& pos, const utils::Coordinate& sp_pos )
{
  utils::Coordinate vol_pos( pos[0] +sp_pos[0], pos[1] +sp_pos[1], pos[2] +sp_pos[2] );
  m_output( vol_pos ) = 1;
}

void GraphExtractor::fillPosition( const Graph::NodePtr& node, const utils::Coordinate& pos, const utils::Coordinate& sp_pos )
{
  utils::Coordinate vol_pos( pos[0] +sp_pos[0], pos[1] +sp_pos[1], pos[2] +sp_pos[2] );
  m_nodes_in_graph( vol_pos ) = node;
}


void GraphExtractor::initVolumeFromGraph( const Graph::NodePtr& node, const double& dim_mult )
{
  fillRadius( node, node->getVal().pos, std::ceil( node->getVal().rad*dim_mult ), std::ceil( node->getVal().rad/2*dim_mult ) );
  for( size_t c_it=0; c_it < node->rank() ; ++c_it )
    initVolumeFromGraph( node->getChild( c_it ), dim_mult );
}


void GraphExtractor::getPathRadius( const utils::Coordinate& pos, Path& path )
{
  path.length = 0;
  path.avg_radius = 0.0;
  size_t it = 0;
  getPathRadiusNode( pos, it, path );
  path.avg_radius /= it;
}


void GraphExtractor::getPathRadiusNode( const utils::Coordinate& pos, size_t& it, Path& path  )
{
  const float& cur_rad = m_cost_map_1( pos );
  ++path.length;
  utils::Coordinate pred_pos = m_neighbor->operator()( pos, m_pred_map_1( pos ) );
  if( pos != pred_pos && m_output( pos ) < 1.0 )
  {
    if( cur_rad > 1.0 )
    {
      ++it;
      path.avg_radius += cur_rad;
      getPathRadiusNode( pred_pos, it, path );
    }
    else getPathRadiusNode( pred_pos, it, path );
  }
}


extern "C" GraphExtractor::Graph* extractGraph( float* input, float* cost_map_1, float* cost_map_2,
                             int* pred_map_1, int* pred_map_2, float* output,
                             int x_dim, int y_dim, int z_dim, int* start_pos,
                             double int_threshold, double cost_cutoff,
                             bool save_grp, char* path )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim ), st_coor(start_pos);
  const Volume v_input( input, shape ), v_cost_1( cost_map_1, shape ), v_cost_2( cost_map_2, shape );
  const VolumeI v_pred_map_1( pred_map_1, shape ), v_pred_map_2( pred_map_2, shape );
  Volume out_arr( output, shape );
  //std::cout << path << std::endl;
  std::string tpath( path  );
  if( tpath == "" ) tpath = "temp.xml";

  std::cout << "Extract Volume using Graph" << std::endl;
  std::cout << "Map Shape: " << v_input.getShape() << std::endl;
  std::cout << "Start Point: " << st_coor << std::endl;
  //std::cout << "Temp File: " << tpath << std::endl;
  GraphExtractor gex( v_input, v_cost_1, v_cost_2, v_pred_map_1, v_pred_map_2, out_arr );
  std::cout << "Inp: " << v_input.min() << " < " << v_input.max() << std::endl;
  GraphExtractor::Graph* graph_ptr = gex.extractGraph( st_coor, int_threshold, cost_cutoff );
  //std::cout << reinterpret_cast<GraphExtractor::Graph*>( graph_ptr )->toXml()  << std::endl;

  //if( save_grp )
    //graph_ptr->saveToFile(tpath);

  return graph_ptr;
}


extern "C" void* extractSkeleton( float* input, float* cost_map_1, float* cost_map_2,
                                  int* pred_map_1, int* pred_map_2, float* output,
                                  int x_dim, int y_dim, int z_dim, int* start_pos,
                                  float* dim_mults, double min_cmb, int dil_sum, int cut_axis, int z_cut, double qp_min_dist,
                                  char* path, void* old_graph_vp = nullptr, bool seed_from_graph= false
                                )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim ), st_coor( start_pos );
  const Volume v_input( input, shape ), v_cost_1( cost_map_1, shape ), v_cost_2( cost_map_2, shape );
  const VolumeI v_pred_map_1( pred_map_1, shape ), v_pred_map_2( pred_map_2, shape );
  Volume out_arr( output, shape );
  utils::CoordinateF c_dim_mults( dim_mults );
  GraphExtractor::Graph* old_graph = reinterpret_cast<GraphExtractor::Graph*>(old_graph_vp);
  std::string tpath( path );
  if( tpath == "" ) tpath = "temp.xml";

  std::cout << "Extract Skeleton" << std::endl;
  std::cout << "Map Shape: " << v_input.getShape() << std::endl;
  std::cout << "Start Point: " << st_coor << std::endl;
  std::cout << "Dim Mults: " << c_dim_mults << std::endl;
  std::cout << "Cutoff: Axis " << cut_axis << ", cut " << z_cut << std::endl;
  GraphExtractor::Cutoff z_cutoff( cut_axis, z_cut );
  std::cout << "init" << std::endl;
  GraphExtractor gex( v_input, v_cost_1, v_cost_2, v_pred_map_1, v_pred_map_2, out_arr );
  //std::cout << "gex" << std::endl;
  GraphExtractor::Graph* graph_ptr = gex.curveSkeletonization( st_coor, z_cutoff, qp_min_dist, c_dim_mults, min_cmb, dil_sum, old_graph, seed_from_graph );
  //std::cout << reinterpret_cast<GraphExtractor::Graph*>( graph_ptr )->toXml()  << std::endl;

  //graph_ptr->saveToFile(tpath);
  //utils::Coordinate pos = graph_ptr->getRoot()->getVal().pos;
  //graph_ptr->zeroRoot();
  //graph_ptr->rotate( utils::CoordinateD(90.0,0.0,0.0) );
  //graph_ptr->translate( pos );

  std::cout << "GRAPH_PTR: " << graph_ptr << std::endl;
  return reinterpret_cast<void*>( graph_ptr );
}


//utils::GridTree* extractGraph()

