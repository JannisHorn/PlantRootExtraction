#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

class ConfigBase:

    def __init__( self ):


cfg = Config()
for key, val in itemize( cfg.__dict__
print(cfg.__dict__)
