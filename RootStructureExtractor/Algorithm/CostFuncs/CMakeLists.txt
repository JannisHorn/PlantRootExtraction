add_library( cost_funcs src/apply_cost_function.cpp )

target_include_directories( cost_funcs PUBLIC
                            "${CMAKE_CURRENT_SOURCE_DIR}/include/"
                            "${RSE_INCLUDE}"
                            "${UTILS_INCLUDE}"
                            )
