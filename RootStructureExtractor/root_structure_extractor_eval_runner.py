#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""
import sys

import Algorithm
import PyUtils    
from evaluation import eval_dataset
import numpy as np
    
    
def main():
    sys.setrecursionlimit(25000)

    distances = [15]
    spacing = 0.1
    int_type = "linear"
    ct_range = []
    gl_range = []
    dil_range = []
    nits_range = []
    nits_mode = "linear"
    ranges = (ct_range, gl_range, dil_range, nits_range, nits_mode)
    
    eval_cfg = {"distances":distances,
                "spacing":spacing}
    
    ipath = "/home/user/horn/segmentation_output/model_LOG1/tube_removed/"
    gtpath = "/home/user/horn/segmentation_output/gt_reshaped_to_match_seg/"
    outfile= "rel_cost"

    ds = eval_dataset.Dataset( ipath, gtpath, outfile )
    ds.build()
    print(ds)
    
    ds( ranges, eval_cfg, 1 )
    

if __name__ == "__main__":
    main()
