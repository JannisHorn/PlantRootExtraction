add_library( graph_pruning src/graph_pruning.cpp )

target_include_directories( graph_pruning PUBLIC
                            "${CMAKE_CURRENT_SOURCE_DIR}/include/"
                            "${RSE_INCLUDE}"
                            "${UTILS_INCLUDE}"
                            )
