add_library( evaluate_graphs src/evaluate_graphs.cpp )

target_include_directories( evaluate_graphs PUBLIC
                            "${CMAKE_CURRENT_SOURCE_DIR}/include/"
                            "${RSE_INCLUDE}"
                            "${UTILS_INCLUDE}"
                            )
