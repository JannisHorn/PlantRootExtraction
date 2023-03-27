#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import numpy as np

def strToNumpyDt( text ):
    if text == "8-Bit":
        return np.uint8
    elif text == "16-Bit signed":
        return np.int16
    elif text == "16-Bit unsigned":
        return np.uint16
    elif text == "32-Bit signed":
        return np.int32
    elif text == "32-Bit unsigned":
        return np.uint32
    elif text == "32-Bit Float":
        return np.float32
    elif text == "64-Bit Float":
        return np.float64
    else:
        return None
