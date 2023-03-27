cmake_minimum_required( VERSION 3.10 )

project( RSE_CLibraries VERSION 0.1.0 )

set( CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/Libs/" )

set( CMAKE_CXX_STANDARD 17 )
set( CMAKE_CXX_STANDARD_REQUIRED TRUE )
set( CMAKE_CXX_FLAGS "-fPIC -o -pthread -O3" )
set( BUILD_SHARED_LIBS TRUE )

set( UTILS_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/Utils/" )
set( RSE_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/Utils/RootExtraction/" )

add_subdirectory( CostFuncs )
add_subdirectory( ShortestPath )
add_subdirectory( ExtractGraph )
add_subdirectory( GraphPruning )
add_subdirectory( GraphRefinement )
if( COMP_EVAL )
  add_subdirectory( EvaluateGraphs )
endif()
