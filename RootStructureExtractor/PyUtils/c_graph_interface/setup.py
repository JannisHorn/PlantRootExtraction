#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

from distutils.core import setup, Extension
import numpy

np_include = numpy.get_include()

module1 = Extension('_c_graph_interface',
                    sources = ['src/c_graph_node.cpp', 'src/c_graph.cpp', 'src/c_graph_interface.cpp' ],
                    include_dirs = [np_include,'include','../../Algorithm/Utils', '../../Algorithm/Utils/RootExtraction'],
                    libraries = ['stdc++'],
                    extra_compile_args = ['-std=c++11', '-fPIC'],
                    language = ['c++'])

setup (name = '_c_graph_interface',
       version = '1.0',
       description = 'Library to extract information from utils::RootGraph structures generated by ExtractRootGraph',
       ext_modules = [module1])
