pyinstaller --onefile \
            --add-bin "Algorithm/Libs/libcost_funcs.so" \
            --add-bin "Algorithm/Libs/libextract_graph.so" \
            --add-bin "Algorithm/Libs/libgraph_pruning.so" \
            --add-bin "Algorithm/Libs/libgraph_refinement.so" \
            --add-bin "Algorithm/Libs/libshortest_path.so" \
            root_extraction.py
