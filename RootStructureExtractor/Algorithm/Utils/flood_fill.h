/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef FLOOD_FILE_H__
#define FLOOD_FILE_H__

#include <volume.h>

namespace utils
{

class FloodFill // No border Check!
{
public:
  FloodFill( Volume& vol ) : m_vol( vol ) {}



private:
  void fillPos( const Coordinate& pos )
  {
    if( m_vol( pos ) >= min_val )
    {
      m_vol( pos ) = new_val;
      fillPos()
    }
  }

  Volume& m_vol;
  float min_val, new_val;
};

}
#endif // FLOOD_FILE_H__

