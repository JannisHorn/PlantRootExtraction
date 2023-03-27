/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef ROOT_GRAPH_H__
#define ROOT_GRAPH_H__

#include "graph.h"
#include "utils.h"
#include "xml_utils.h"
#include <fstream>
#include <clocale>
#include "volume.h"
#include "sphere_mask.h"

namespace utils
{
struct RootNode
{
  utils::Coordinate pos;
  float rad;
  size_t branch_id;

  RootNode() : pos( 0,0,0 ), rad(0), branch_id(0) {};
  RootNode( const utils::Coordinate& n_pos, const float& n_rad=1.f, const size_t& br_id=0 )
    : pos( n_pos ), rad( n_rad ), branch_id( br_id ) {}
  RootNode( const RootNode& other ) : pos( other.pos ), rad( other.rad ), branch_id( other.branch_id ) {}

  std::string toString()
  {
    return pos.toString();
  }

  void rotate( const CoordinateD& to_x, const CoordinateD& to_y, const CoordinateD& to_z )
  {
    const int x = std::round( pos[0]*to_x[0] +pos[1]*to_x[1] +pos[2]*to_x[2] );
    const int y = std::round( pos[0]*to_y[0] +pos[1]*to_y[1] +pos[2]*to_y[2] );
    const int z = std::round( pos[0]*to_z[0] +pos[1]*to_z[1] +pos[2]*to_z[2] );
    pos = Coordinate( x,y,z );
  }

  void translate( const CoordinateD& translation )
  {
    pos = Coordinate( pos[0] +translation[0], pos[1] +translation[1], pos[2] +translation[2] );
  }

  template<typename _Tp>
  void fillVolume( VolumeBase<_Tp>& out, const std::vector<Volume>& spheres, const _Tp& val, const double& rrate ) const
  {
    int radius = int( round( rad *rrate ) );
    const int min_it = pos.min() -radius;
    const int max_it = (out.getShape() +(pos +radius).scale(-1)).min();
    int border = std::min( min_it, max_it );
    if( border < 0 )
      radius += border;

    //std::cout << "shape: " << out.getShape() << ", other: " << (pos +radius).scale(-1) << std::endl;
    //std::cout << "Rad: " << rad << ", PosMin: " << pos.min() << ", PosMax: " << pos.max() << std::endl;
    //std::cout << "Min: " << min_it << ", Max: " << max_it << ", outmax: " << out.getShape()[pos.argmax()] << std::endl;
    //std::cout << "Pos: " << pos << ", Radius: " << radius << std::endl;
    const size_t diameter = radius *2 +1;
    const Volume& sphere = spheres[radius];
    for( size_t z=0; z <= radius ; ++z )
      for( size_t y=0; y <= radius ; ++y )
        for( size_t x=0; x <= radius ; ++x )
        {
          if( sphere( x,y,z ) > 0.0 )
          {
            Coordinate anchor = Coordinate( pos[0]-radius,pos[1]-radius,pos[2]-radius );
            const size_t c_x = diameter -x -1;
            const size_t c_y = diameter -y -1;
            const size_t c_z = diameter -z -1;
            //std::cout << "rad:" << rad << ": " << anchor << "->" << x << "," << y << "," << z << " ; ";
            fillOutput<_Tp>( out, anchor, Coordinate( x, y, z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( x, y, c_z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( x, c_y, z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( x, c_y, c_z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( c_x, y, z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( c_x, y, c_z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( c_x, c_y, z ), val );
            fillOutput<_Tp>( out, anchor, Coordinate( c_x, c_y, c_z ), val );
          }
        }
  }

  template<typename _Tp>
  void fillOutput( VolumeBase<_Tp>& out, const Coordinate& anchor, const Coordinate& sp_pos, const _Tp& val ) const
  {
    Coordinate vol_pos( anchor[0] +sp_pos[0], anchor[1] +sp_pos[1], anchor[2] +sp_pos[2] );
    out( vol_pos ) = val;
  }

};

class RootGraph : public GridTree<RootNode>
{
public:
  RootGraph() : GridTree() {}
  RootGraph( const NodePtr node ) : GridTree( node ) {};

  std::string toXml()
  {
    m_id = 0;
    xml::Document xml_tree( "Forest" );
    xml_tree.getRoot().addElement( nodeToXml( getRoot() ) );
    return xml_tree.toString();
  }

  xml::Element* nodeToXml( const NodePtr node )
  {
    xml::Element* xml_node = new xml::Element( "Node" );
    xml_node->addAttribute( "id", std::to_string( m_id ) );
    ++m_id;
    xml_node->addAttribute( "bo", std::to_string( node->getVal().branch_id ) );
    xml_node->addAttribute( "rad", std::to_string( node->getVal().rad ) );
    xml_node->addAttribute( "x", std::to_string( node->getVal().pos[0] ) );
    xml_node->addAttribute( "y", std::to_string( node->getVal().pos[1] ) );
    xml_node->addAttribute( "z", std::to_string( node->getVal().pos[2] ) );
    for( size_t it=0; it<node->getChilds().size(); ++it )
    {
      const NodePtr child = node->getChilds()[it];
      xml_node->addElement( nodeToXml( child ) );
    }
    return xml_node;
  }

  /**
   * Recursively create xml nodes and save to file_stream
   *
   * @param f_name File path to write to.
   */
  void saveToFile( const std::string& f_name )
  {
    std::setlocale( LC_ALL, "C" );
    std::cout << "Saving to " << f_name << std::endl;
    std::ofstream f_out( f_name );
    f_out << toXml();
    f_out.close();
  }


  /// Search graph recursively to find largest radius. @return max radius as float.
  float getMaxRad() const
  {
    return getMaxRadNode( m_root );
  }


  /**
   * Create rotation Matrix and rotate graph recursively around (0,0,0).
   *
   * @param angles_in_degree/ a,b,c Angle vector / 3 angles used for rotation
   */
  void rotate( const CoordinateD& angles_in_degree )
  {
    rotate( angles_in_degree[0], angles_in_degree[1], angles_in_degree[2] );
  }
  void rotate( const double a, const double b, const double c )
  {
    double a_rad = a *rad_mult,
           b_rad = b *rad_mult,
           c_rad = c *rad_mult;
    const double cos_a = std::cos( a_rad ), sin_a = std::sin( a_rad );
    const double cos_b = std::cos( b_rad ), sin_b = std::sin( b_rad );
    const double cos_c = std::cos( c_rad ), sin_c = std::sin( c_rad );

    const CoordinateD to_x( cos_a*cos_b,
                            cos_a*sin_b*sin_c - sin_a*cos_c,
                            cos_a*sin_b*cos_c + sin_a*sin_c );
    const CoordinateD to_y( sin_a*cos_b,
                            sin_a*sin_b*sin_c + cos_a*cos_c,
                            sin_a*sin_b*cos_c - cos_a*sin_c );
    const CoordinateD to_z( -sin_b,
                            cos_b*sin_c,
                            cos_b*cos_c );

    rotateNode( m_root, to_x, to_y, to_z );
  }


  /**
   * Translate graph recursively per node given translation vector.
   *
   * @param translation, translation_int Vector to translate graph.
   */
  void translate( const CoordinateD& translation )
  {
    translateNode( m_root, translation );
  }
  void translate( const Coordinate& translation_int )
  {
    const CoordinateD translation( static_cast<double>(translation_int[0]),
                                   static_cast<double>(translation_int[1]),
                                   static_cast<double>(translation_int[2]) );
    translateNode( m_root, translation );
  }


  /**
   * Set node to (0,0,0) and translate graph accordingly
   */
  void zeroRoot()
  {
    translate( m_root->getVal().pos.scale(-1.0) );
  }


  /**
   * Reevaluate rood ids to repair non unique branches/ inconsistencies in added branches
   */
  void evaluateRootID()
  {
    evaluateRootIDNode( m_root, 1 );
  }


  /**
   * Repair elements of radius ~1 by running average interpolation
   */
  void repairRadius()
  {
    repairRadiusNode( m_root, m_root->getVal().rad, 0.0 );
  }


  /**
   * Repair root tip radii s.t. radius > 0.0 for all nodes.
   */
  void repairRootTips()
  {
    repairTipRadiusNode( m_root, m_root->getVal().rad );
  }


  /**
   * Rotate nodes around given anchor.
   *
   * @param point Anchor to rotate around.
   * @param angles 3D Angles around which to rotate.
   */
  void rotateAround( const CoordinateD& point, const CoordinateD& angles )
  {
    translate( point.scale(-1) );
    rotate( angles );
    translate( point );
  }


  /**
   * Draw graph as continous lines on input volume.
   * Calls drawing recursively on all nodes.
   *
   * @param[out] canvas Volume to be drawn on.
   */
  void draw( Volume& canvas ) const
  {
    drawNode( m_root, canvas );
  }


  /**
   * Create sphere masks.
   * Recursive call to fill volume with arbitrary value.
   *
   * @param[out] out Volume to be filled.
   * @param[in] dim_facs Scale of each dimension for sphere generation.
   * @param[in] val Value used to fill graph.
   * @param[in] rrate Rate by which to dilate graph radius.
   */
  void fillVolume( Volume& out, const CoordinateD& dim_facs, const float& val=0.f, const double& rrate=1.0 ) const
  {
    //std::cout << "Entered" << std::endl;
    float max_rad = getMaxRad();
    std::vector<Volume> spheres;
    spheres.reserve( max_rad+1 );
    for( size_t r_it=0; r_it <= max_rad; ++r_it )
    {
      Volume sphere;
      sphereMask( sphere, r_it, dim_facs );
      spheres.push_back( std::move( sphere ) );
    }
    //std::cout << "Node it" << std::endl;
    fillVolumeNode( m_root, spheres, out, val, rrate );
  }


  /**
   * Recursive call to get all positions of graph vertices.
   *
   * @param[out] out Vector holding positions for all vetices in graph
   */
  void getPoints( std::vector<utils::Coordinate>& out_vec ) const
  {
    out_vec.clear();
    out_vec.reserve( size() );
    getPointsNode( m_root, out_vec );
  }


  /**
   * Recursive call to get dense points from all line segments.
   * Take line parent_node->this, sample points along line with dist mdist
   * fill list_out with start points of each subsection.
   *
   * @param[out] out Vector holding vectors of double points for each line segment
   * @param[in] mdist Double for maximum distant between dense line points
   */
  void getDensePointList( std::vector<std::vector<utils::CoordinateD>>& list_out, const double& max_dist ) const
  {
    list_out.push_back( std::vector<utils::CoordinateD>{ m_root->getVal().pos.toType<double>() } );
    for( const NodePtr& child : m_root->getChilds() )
      getDensePointsNode( m_root, child, list_out, max_dist );
  }


private:
  float getMaxRadNode( NodePtr cur_node ) const
  {
    float max_rad = cur_node->getVal().rad;
    for( size_t c_it=0; c_it < cur_node->rank() ; ++c_it )
      max_rad = std::max( max_rad, getMaxRadNode( cur_node->getChild(c_it) ) );
    return max_rad;
  }

  void rotateNode( NodePtr cur_node, const CoordinateD& to_x,
                   const CoordinateD& to_y, const CoordinateD& to_z )
  {
    cur_node->getVal().rotate( to_x, to_y, to_z );
    for( size_t it=0; it<cur_node->getChilds().size(); ++it )
      rotateNode( cur_node->getChilds()[it], to_x, to_y, to_z );
  }

  void translateNode( NodePtr cur_node, const CoordinateD& translation )
  {
    cur_node->getVal().translate( translation );
    for( size_t it=0; it<cur_node->getChilds().size(); ++it )
      translateNode( cur_node->getChilds()[it], translation );
  }

  void drawNode( const NodePtr& cur_node, Volume& canvas ) const
  {
    for( size_t c_it=0; c_it < cur_node->rank() ; ++c_it )
    {
      canvas.drawLine( cur_node->getVal().pos, cur_node->getChild( c_it )->getVal().pos, 1.f );
      drawNode( cur_node->getChild( c_it ), canvas );
    }
  }

  void fillVolumeNode( const NodePtr& cur_node, const std::vector<Volume>& spheres,
                       Volume& out, const float& val=0.f, const double& rrate=1.0 ) const
  {
    cur_node->getVal().fillVolume<float>( out, spheres, val, rrate );
    for( size_t c_it=0; c_it < cur_node->rank() ; ++c_it )
      fillVolumeNode( cur_node->getChild(c_it), spheres, out, val, rrate );
  }

  void fillVolumeWithPtr( const NodePtr& cur_node, const std::vector<Volume>& spheres,
                          VolumeBase<void*>& out, const double& rrate=1.0 ) const
  {
    cur_node->getVal().fillVolume<void*>( out, spheres, reinterpret_cast<void*>( cur_node ), rrate );
    for( size_t c_it=0; c_it < cur_node->rank() ; ++c_it )
      fillVolumeWithPtr( cur_node->getChild(c_it), spheres, out, rrate );
  }

  void getPointsNode( const NodePtr& cur_node, std::vector<utils::Coordinate>& out_vec ) const
  {
    out_vec.push_back( cur_node->getVal().pos );
    for( size_t c_it=0 ; c_it < cur_node->rank() ; ++c_it )
      getPointsNode( cur_node->getChild( c_it ), out_vec );
  }

  void getDensePointsNode( const NodePtr& pred_node, const NodePtr& cur_node, std::vector<std::vector<utils::CoordinateD>>& out , const double& mdist ) const
  {
    utils::Line f( pred_node->getVal().pos, cur_node->getVal().pos );
    f.normalize();
    f.scale( mdist );
    out.push_back( std::vector<utils::CoordinateD>() );
    std::vector<utils::CoordinateD>& vec = out.back();
    vec.reserve( std::ceil( f.len+1 ) );
    double x = 1.0;
    while ( x <= f.len )
    {
      vec.push_back( f(x) );
      ++x;
    }
    vec.push_back( cur_node->getVal().pos );

    for( size_t c_it=0 ; c_it < cur_node->rank() ; ++c_it )
      getDensePointsNode( cur_node, cur_node->getChild( c_it ), out, mdist );
  }


  size_t evaluateRootIDNode( const NodePtr& cur_node, const size_t& cur_id )
  {
    size_t id = cur_id;
    cur_node->getVal().branch_id = id;
    for( size_t c_it=0 ; c_it < cur_node->rank() ; ++c_it )
      id = evaluateRootIDNode( cur_node->getChild( c_it ), id );
    if( cur_node->rank() == 0 )
      return id +1;
    else
      return id;
  }


  float repairRadiusNode( const NodePtr& cur_node, const float& last_rad, const double& con_it )
  {
    if( cur_node->rank() == 0 )
      return cur_node->getVal().rad;
      //if( cur_node->getVal().rad < 0.5 )
      //  cur_node->getVal().rad = last_rad;
      //return last_rad;
    if( cur_node->getVal().rad <= 1.5 )
    {
      const float next_rad = repairRadiusNode( cur_node->getChild( 0 ), last_rad, con_it+1 );
      const float new_rad = (con_it/(con_it+1)) *next_rad +(1/(con_it+1)) *last_rad;
      cur_node->getVal().rad = new_rad;
      for( size_t c_it=1 ; c_it < cur_node->rank() ; ++c_it )
        repairRadiusNode( cur_node->getChild( c_it ), last_rad, con_it+1 );
      return new_rad;
    }
    else
    {
      float& cur_rad = cur_node->getVal().rad;
      for( size_t c_it=0 ; c_it < cur_node->rank() ; ++c_it )
        repairRadiusNode( cur_node->getChild( c_it ), cur_rad, 0.0 );
      return cur_rad;
    }
  }


  void repairTipRadiusNode( NodePtr cur_node, float last_rad )
  {
    if( cur_node->rank() == 0
        && cur_node->getVal().rad < last_rad )
      cur_node->getVal().rad = last_rad;
    else
    {
      float cur_rad = cur_node->getVal().rad;
      for( size_t c_it=0 ; c_it < cur_node->rank() ; ++c_it )
        repairTipRadiusNode( cur_node->getChild( c_it ), cur_rad );
    }
  }


  size_t m_id = 0;
  static constexpr double rad_mult = M_PI/180.0;
};
}

#endif // ROOT_GRAPH_H__

