add_library( extract_graph src/extract_graph.cpp )

target_include_directories( extract_graph PUBLIC
                            "${CMAKE_CURRENT_SOURCE_DIR}/include/"
                            "${RSE_INCLUDE}"
                            "${UTILS_INCLUDE}"
                            )
