#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 01:08:42 2019

@author: jhorn
"""

from distutils.core import setup, Extension
import numpy

np_include = numpy.get_include()

module1 = Extension('_cpython_helper',
                    sources = ['cpython_helper.cpp' ],
                    include_dirs = [np_include,'include','../../Algorithm/Utils', '../../Algorithm/Utils/RootExtraction'],
                    libraries = ['stdc++'],
                    extra_compile_args = ['-std=c++11', '-fPIC'],
                    language = ['c++'])

setup (name = '_cpython_helper',
       version = '1.0',
       description = 'Helper library for c -> python type conversions',
       ext_modules = [module1])

