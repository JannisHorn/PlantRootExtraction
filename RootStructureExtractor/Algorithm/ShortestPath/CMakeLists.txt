set( LIBRARY_OUTPUT_DIRECTORY )

add_library( shortest_path src/adapted_djikstra.cpp )

target_include_directories( shortest_path PUBLIC
                            "${CMAKE_CURRENT_SOURCE_DIR}/include/"
                            "${RSE_INCLUDE}"
                            "${UTILS_INCLUDE}"
                            )
