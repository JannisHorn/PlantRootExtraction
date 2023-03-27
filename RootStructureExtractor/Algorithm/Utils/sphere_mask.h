/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef SPHERE_MASK_H__
#define SPHERE_MASK_H__

#include "volume.h"

inline void sphereMask( Volume& output, const size_t radius, const utils::CoordinateF& dim_facs )
{
  size_t diameter = radius *2 +1;
  if( diameter == 0 )
  {
    output = std::move( Volume( 1,1,1 ) );
    output( 0,0,0 ) = 1;
    return;
  }
  output = std::move( Volume( diameter, diameter, diameter ) );
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

#endif // SPHERE_MASK_H__
