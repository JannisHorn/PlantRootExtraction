cmake_minimum_required( VERSION 3.10 )

project( RootStructureExtractor VERSION 0.1 )

set( CMAKE_CXX_STANDARD 17 )
set( CMAKE_CXX_STANDARD_REQUIRED TRUE )

option( COMP_EVAL "Compile graph evaluation c++ library" OFF )

add_subdirectory( Algorithm )
