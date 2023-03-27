add_library( graph_refinement src/graph_refinement.cpp )

target_include_directories( graph_refinement PUBLIC
                            "${CMAKE_CURRENT_SOURCE_DIR}/include/"
                            "${RSE_INCLUDE}"
                            "${UTILS_INCLUDE}"
                            )
