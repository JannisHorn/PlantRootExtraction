/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#include <vector>
#include <iostream>
#include <thread>

#include "apply_cost_function.h"

SphereFitCost::SphereFitCost( const Volume& input, Volume& output )
: m_input( input ), m_output( output )
{
}

inline int strPt( const int st, const int rad ) { return -std::min( 0, st-rad ); } //TODO fix incorrect start comp

void SphereFitCost::fitSpheresThread( const double min_occ, const double sphere_min_occ )
{
  int z = m_output.multithreadAccess();
  utils::Coordinate shape = m_input.getShape();
  while( z != -1 )
  {
    //if ( shape[1] %z == 0 )
    std::cout << z << "/" << shape[2] << "\r";
    int num_spheres = m_spheres.size();
    int sphere_it = 1; // Use as running variable -> next element r_new : r_old -1 =< r_new => r_old +1
    size_t cut_x_1 = num_spheres, cut_y_1 = num_spheres;
    size_t cut_x_2 = shape[0] -num_spheres, cut_y_2 = shape[1] -num_spheres;
    std::vector<int> z_mins, z_maxs, z_starts;
    for( int it=0; it < m_spheres.size() ; ++it )
    {
      z_mins.push_back( std::max( 0, z -it ) );
      z_maxs.push_back( std::min( z +it +1, shape[2] ) ); // TODO CORRECT START COMPUTATION!!!
      z_starts.push_back( strPt( z, it ) );
    }
    for( int y=0; y < shape[1] ; ++y )
    {
      std::vector<int> y_mins, y_maxs, y_starts;
      for( int it=0; it < m_spheres.size() ; ++it )
      {
        y_mins.push_back( std::max( 0, y -it ) );
        y_maxs.push_back( std::min( y +it +1, shape[1] ) ); // TODO CORRECT START COMPUTATION!!!
        y_starts.push_back( strPt( y, it ) );
      }
      for( int x=0; x < shape[0] ; ++x )
      {
        double occ = 1.0;
        while( sphere_it < m_spheres.size() )
        {
          utils::Coordinate mins( std::max( 0, x -sphere_it ), y_mins[sphere_it], z_mins[sphere_it] );
          utils::Coordinate maxs( std::min( x +sphere_it +1, shape[0] ), y_maxs[sphere_it], z_maxs[sphere_it] );
          utils::Coordinate str_pt( strPt( x, sphere_it ), y_starts[sphere_it], z_starts[sphere_it] );
          occ = fitSphere( sphere_it, min_occ, str_pt, mins, maxs ) /m_sphere_sums[sphere_it];
          if( occ < sphere_min_occ )
            break;
          //std::cout << sphere_it << ":" << occ << "<-" << m_sphere_sums[sphere_it] << std::endl;
          ++sphere_it;
        }
        m_output( x,y,z ) = sphere_it-1;
        sphere_it = 1;
      }
    }
    z = m_output.multithreadAccess();
  }
}


void SphereFitCost::fitCirclesThread( const double min_occ, const double sphere_min_occ )
{
  utils::Coordinate shape = m_input.getShape();
  //std::cout << "Enter " << shape << std::endl;
  int num_spheres = m_spheres.size();
  int sphere_it = 1; // Use as running variable -> next element r_new : r_old -1 =< r_new => r_old +1
  size_t cut_x_1 = num_spheres, cut_y_1 = num_spheres;
  size_t cut_x_2 = shape[0] -num_spheres, cut_y_2 = shape[1] -num_spheres;
  for( int y=0; y < shape[1] ; ++y )
  {
    std::vector<int> y_mins, y_maxs, y_starts;
    for( int it=0; it < m_spheres.size() ; ++it )
    {
      y_mins.push_back( std::max( 0, y -it ) );
      y_maxs.push_back( std::min( y +it +1, shape[1] ) ); // TODO CORRECT START COMPUTATION!!!
      y_starts.push_back( strPt( y, it ) );
    }
    for( int x=0; x < shape[0] ; ++x )
    {
      double occ = 1.0;
      while( sphere_it < m_spheres.size() )
      {
        utils::Coordinate mins( std::max( 0, x -sphere_it ), y_mins[sphere_it], 0 );
        utils::Coordinate maxs( std::min( x +sphere_it +1, shape[0] ), y_maxs[sphere_it], 1 );
        utils::Coordinate str_pt( strPt( x, sphere_it ), y_starts[sphere_it], 0 );
        //if(m_input(x,y,0) > 0.0)std::cout << "int:" << x << "," << y << ":" << m_input(x,y,int(0)) << std::endl;
        occ = fitCircle( sphere_it, min_occ, str_pt, mins, maxs ) /m_sphere_sums[sphere_it];
        if( occ < sphere_min_occ )
          break;
        //std::cout << sphere_it << ":" << occ << "<-" << m_sphere_sums[sphere_it] << std::endl;
        ++sphere_it;
      }
      m_output( x,y,0 ) = sphere_it-1;
      sphere_it = 1;
    }
  }
}


void SphereFitCost::applySphereCost( const double min_occ, const double sphere_min_occ,
                                     const size_t sphere_max_rad, const utils::CoordinateF& dim_facs,
                                     const int max_threads )
{
  m_spheres.reserve( sphere_max_rad+1 );
  for( size_t r_it=0; r_it <= sphere_max_rad ; ++r_it )
  {
    Volume sphere;
    createSphereMask( sphere, r_it, dim_facs );
    m_sphere_sums.push_back( sphere.sum() );
    m_spheres.push_back( std::move( sphere ) );
  }
  applyCost( min_occ, sphere_min_occ, dim_facs, max_threads );
}


void SphereFitCost::applyCircleCost( const double min_occ, const double sphere_min_occ,
                                     const size_t sphere_max_rad, const utils::CoordinateF& dim_facs,
                                     const int max_threads )
{
  m_spheres.reserve( sphere_max_rad+1 );
  for( size_t r_it=0; r_it <= sphere_max_rad ; ++r_it )
  {
    Volume sphere;
    createCircleMask( sphere, r_it, dim_facs );
    //std::cout << sphere << std::endl;
    m_sphere_sums.push_back( sphere.sum() );
    m_spheres.push_back( std::move( sphere ) );
  }
  fitCirclesThread( min_occ, sphere_min_occ );
}


void SphereFitCost::applyCost( const double min_occ, const double sphere_min_occ,
                               const utils::CoordinateF& dim_facs, const int max_threads )
{
  std::vector<std::thread> fitting_threads;
  for( size_t t_it=0; t_it < max_threads ; ++t_it )
    fitting_threads.push_back( std::thread( &SphereFitCost::fitSpheresThread, this, min_occ, sphere_min_occ ) );
  for( size_t t_it=0; t_it < max_threads ; ++t_it )
    fitting_threads[t_it].join();

  std::cout << std::endl;
}


void SphereFitCost::createSphereMask( Volume& output, const size_t radius, const utils::CoordinateF& dim_facs )
{
  size_t diameter = radius *2 +1;
  if( diameter == 0 )
  {
    output = std::move( Volume( 1,1,1 ) );
    output( 0,0,0 ) = 1;
    return;
  }
  output = Volume( diameter, diameter, diameter );
  const utils::Coordinate center( radius, radius, radius );
  const double sqrd_rad = std::pow( radius, 2 );
  for( size_t x_it=0; x_it < radius +1; ++x_it )
    for( size_t y_it=0; y_it < radius +1; ++y_it )
      for( size_t z_it=0; z_it < radius +1; ++z_it )
        if( center.getSqrdDistance( utils::Coordinate( x_it, y_it, z_it ), dim_facs ) <= sqrd_rad )
        {
          const size_t c_x = diameter -x_it -1;
          const size_t c_y = diameter -y_it -1;
          const size_t c_z = diameter -z_it -1;
          output( x_it, y_it, z_it ) = 1.0;
          output( x_it, y_it, c_z ) = 1.0;
          output( x_it, c_y, z_it ) = 1.0;
          output( x_it, c_y, c_z ) = 1.0;
          output( c_x, y_it, z_it ) = 1.0;
          output( c_x, y_it, c_z ) = 1.0;
          output( c_x, c_y, z_it ) = 1.0;
          output( c_x, c_y, c_z ) = 1.0;
        }
}


void SphereFitCost::createCircleMask( Volume& output, const size_t radius, const utils::CoordinateF& dim_facs, const size_t& dim )
{
  size_t diameter = radius *2 +1;
  if( diameter == 0 )
  {
    output = std::move( Volume( 1,1,1 ) );
    output( 0,0,0 ) = 1;
    return;
  }
  output = Volume( diameter, diameter, 1 );
  const utils::Coordinate center( radius, radius, 0 );
  const double sqrd_rad = std::pow( radius, 2 );
  for( size_t x_it=0; x_it < radius +1; ++x_it )
    for( size_t y_it=0; y_it < radius +1; ++y_it )
      if( center.getSqrdDistance( utils::Coordinate( x_it, y_it, 0 ), dim_facs ) <= sqrd_rad )
      {
        const size_t c_x = diameter -x_it -1;
        const size_t c_y = diameter -y_it -1;
        output( x_it, y_it, size_t(0) ) = 1.0;
        output( x_it, c_y, size_t(0) ) = 1.0;
        output( c_x, y_it, size_t(0) ) = 1.0;
        output( c_x, c_y, size_t(0) ) = 1.0;
      }
}


extern "C" int applySphereCost( float* input, float* output, int x_dim, int y_dim, int z_dim,
                                double min_occ, double min_sphere_occ, int sphere_max_rad,
                                float* dim_facs, int num_threads )
{
  std::cout << "MinOcc=" << min_occ << " minSphereOcc=" << min_sphere_occ << std::endl;
  utils::Coordinate shape( x_dim, y_dim, z_dim );
  Volume input_arr( input, shape ), output_arr( output, shape );
  //std::cout << input_arr << std::endl;
  std::cout << input_arr.getShape() << "->"<< output_arr.getShape() << std::endl;
  SphereFitCost cost( input_arr, output_arr );
  cost.applySphereCost( min_occ, min_sphere_occ, sphere_max_rad, utils::CoordinateF( dim_facs ), num_threads );
  return 0;
}


extern "C" int applyCircleCost( float* input, float* output, int x_dim, int y_dim, int z_dim,
                                double min_occ, double min_sphere_occ, int sphere_max_rad,
                                float* dim_facs, int num_threads )
{
  std::cout << "MinOcc=" << min_occ << " minSphereOcc=" << min_sphere_occ << std::endl;
  utils::Coordinate shape( x_dim, y_dim, z_dim );
  Volume input_arr( input, shape ), output_arr( output, shape );
  //std::cout << input_arr << std::endl;
  std::cout << input_arr.getShape() << "->"<< output_arr.getShape() << std::endl;
  std::cout << "Max " << input_arr.max() << std::endl;
  SphereFitCost cost( input_arr, output_arr );
  cost.applyCircleCost( min_occ, min_sphere_occ, sphere_max_rad, utils::CoordinateF( dim_facs ), num_threads );
  return 0;
}




RadiusConvolutionCost::RadiusConvolutionCost( const Volume& input, Volume& output )
: m_input( input ), m_output( output ) {}


void RadiusConvolutionCost::apply( const int& mask_size, const size_t& max_threads )
{
  m_mask_size = mask_size;
  m_mask_num_el = std::pow( m_mask_size*2+1, 3 );
  m_output.resetAccess();
  std::vector<std::thread> threads;
  for( size_t t_iz=0; t_iz < max_threads ; ++t_iz )
    threads.push_back( std::thread( &RadiusConvolutionCost::threadRunner, this ) );
  for( size_t t_it=0; t_it < max_threads ; ++t_it )
    threads[t_it].join();
}


void RadiusConvolutionCost::threadRunner()
{
  int z = m_output.multithreadAccess();
  while( z != -1 )
  {
    for( int y=0; y < m_output.getShape()[1]; ++y )
    {
      for( int x=0; x < m_output.getShape()[0]; ++x )
      {
        m_output( x,y,z ) = maskLocalRadius( x,y,z );
      }
    }
    z = m_output.multithreadAccessOffset( m_mask_size );
  }
}


float RadiusConvolutionCost::maskLocalRadius( const int& x,
                                              const int& y,
                                              const int& z )
{
  float sum = 0;
  const utils::Coordinate &shape = m_output.getShape();
  const utils::Coordinate mins( std::max( 0, x-m_mask_size ), std::max( 0, y-m_mask_size ), std::max( 0, z-m_mask_size ) );
  const utils::Coordinate maxs( std::min( shape[0], x+m_mask_size ), std::min( shape[1], y+m_mask_size ), std::min( shape[2], z+m_mask_size ) );
  const float& c_val = m_input(x,y,z);
  for( int z_it=mins[2]; z_it < maxs[2] ; ++z_it )
    for( int y_it=mins[1]; y_it < maxs[1] ; ++y_it )
      for( int x_it=mins[0]; x_it < maxs[0] ; ++x_it )
        if( m_input( x_it, y_it, z_it ) < c_val ) sum += 1;
  int num_elems = ( maxs[0]-mins[0] ) *( maxs[1]-mins[1] ) *( maxs[2]-mins[2] );
  return sum /num_elems;
}


extern "C" int applyRadiusCost( float* input, float* output, int x_dim, int y_dim, int z_dim,
                                int mask_size, int num_threads )
{
  utils::Coordinate shape( x_dim, y_dim, z_dim );
  Volume input_arr( input, shape ), output_arr( output, shape );
  //std::cout << input_arr << std::endl;
  std::cout << input_arr.getSize() << "->"<< output_arr.getSize() << std::endl;
  RadiusConvolutionCost cost( input_arr, output_arr );
  cost.apply( mask_size, num_threads );
  return 0;
}



//extern "C" void applyRadiusConsistentCost( float* gp_pts, float* radius, int num_gps,
//                                           int x_dim, int y_dim, int z_dim, int num_threads )
