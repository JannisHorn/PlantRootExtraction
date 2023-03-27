/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef COST_FUNCTION_H__
#define COST_FUNCTION_H__

#include "utils.h"
#include "volume.h"
#include <thread>

class SphereFitCost
{
public:
  SphereFitCost( const Volume& input, Volume& output );
  //~SphereFitCost() { for( size_t it=0; it < m_spheres.size() ; ++it ) delete m_spheres[it]; }
  void applySphereCost( const double min_occ, const double sphere_min_occ,
                        const size_t sphere_max_rad, const utils::CoordinateF& dim_facs,
                        const int max_threads=4 );
  void applyCircleCost( const double min_occ, const double sphere_min_occ,
                        const size_t sphere_max_rad, const utils::CoordinateF& dim_facs,
                        const int max_threads=4 );
  void createSphereMask( Volume& output, const size_t radius, const utils::CoordinateF& dim_facs );
  void createCircleMask( Volume& output, const size_t radius, const utils::CoordinateF& dim_facs, const size_t& dim=2 );

private:
  //void createSphereMask( Volume& output, const size_t radius );
  void applyCost( const double min_occ, const double sphere_min_occ,
                  const utils::CoordinateF& dim_facs, const int max_threads=4 );
  void fitSpheresThread( const double min_occ, const double sphere_min_occ );
  void fitCirclesThread( const double min_occ, const double circle_min_occ );

  inline double fitSphere( const size_t sph_it, const double min_occ, const utils::Coordinate& str_ptr,
                           const utils::Coordinate& mins, const utils::Coordinate& maxs ) const
  {
    //std::cout << sph_it << ": " << std::endl;
    int mask_x = str_ptr[0]; int mask_y = str_ptr[1]; int mask_z = str_ptr[2];
    float occ_val = 0.f;
    for( size_t z=mins[2]; z < maxs[2] ; ++z )
    {
      for( size_t y=mins[1]; y < maxs[1] ; ++y )
      {
        for( size_t x=mins[0]; x < maxs[0] ; ++x )
        {
          if( m_input(x,y,z) >= min_occ )
          {
            //std::cout << "(" << mask_x << "," << mask_y << "," << mask_z << " = " << m_spheres[sph_it](mask_x, mask_y, mask_z) << ") ";
            occ_val += m_spheres[sph_it](mask_x, mask_y, mask_z);
            //std::cout << occ_val << std::endl;
          }
          ++mask_x;
        }
        mask_x = str_ptr[0];
        ++mask_y;
      }
      mask_y = str_ptr[1];
      ++mask_z;
    }
    //if(occ_val>0.0) std::cout << " = "  << occ_val << std::endl;
    return occ_val;
  }


  inline double fitCircle( const size_t sph_it, const double min_occ, const utils::Coordinate& str_ptr,
                           const utils::Coordinate& mins, const utils::Coordinate& maxs )
  {
    int mask_x = str_ptr[0]; int mask_y = str_ptr[1]; int mask_z = 0;
    float occ_val = 0.f;
    for( size_t y=mins[1] ; y < maxs[1] ; ++y )
    {
      for( size_t x=mins[0] ; x < maxs[0] ; ++x )
      {
        //std::cout << x << "," << y << ":" << m_input(x,y,size_t(0)) << "; " << mask_x << "," << mask_y << ":" << m_spheres[sph_it](mask_x, mask_y, mask_z) << std::endl;
        if( m_input(x,y,size_t(0) ) >= min_occ )
        {
          occ_val += m_spheres[sph_it](mask_x, mask_y, mask_z);
        }
        ++mask_x;
      }
      mask_x = str_ptr[0];
      ++mask_y;
    }
    return occ_val;
  }


  const Volume &m_input;
  Volume &m_output;
  std::vector<Volume> m_spheres;
  std::vector<float> m_sphere_sums;
};




class RadiusConvolutionCost
{
public:
  RadiusConvolutionCost( const Volume& input, Volume& output );

  void apply( const int& mask_size, const size_t& max_threads=4 );
private:
  void threadRunner();
  float maskLocalRadius( const int& x, const int& y,const int& z );

  const Volume &m_input;
  Volume &m_output;
  int m_mask_size;
  float m_mask_num_el;
};



#endif // COST_FUNCTION_H__

