#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Jannis Horn - All Rights Reserved
You may use, distribute and modify this code under the
terms of the GNU GENERAL PUBLIC LICENSE Version 3.
"""

import numpy as np
import sys
import os
import math
import argparse
from copy import deepcopy
from time import time


def point_distance_Euclidean(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def dfs_tree(node, point_list, parent_node, min_dist=None):
    x, y, z = node.getCoorAsFloat()

    if parent_node is None:  # this is the root node
        # print('Current node is root')
        #assert len(node.getChildren()) == 1  # assert the root node only have 1 child
        child = node.getChildren()[0]
        c_x, c_y, c_z = child.getCoorAsFloat()
        direction_x, direction_y, direction_z = (
        c_x - x, c_y - y, c_z - z)  # the same direction as the segment that starts with the root
        point_list.append([len(point_list), x, y, z, direction_x, direction_y, direction_z])

    else:
        # print('Current node is not root')
        # add the intermediate points between the parent and current node
        p_x, p_y, p_z = parent_node.getCoorAsFloat()
        direction_x, direction_y, direction_z = (x - p_x, y - p_y, z - p_z)
        seg_length = point_distance_Euclidean(node.getCoor(), parent_node.getCoor())
        #         print('length of current segment:', seg_length)
        if min_dist is not None:
            if seg_length > min_dist:  # then this segment should contain some intermediate points
                if seg_length % min_dist == 0:
                    num_inter_points = seg_length // min_dist - 1
                else:
                    num_inter_points = seg_length // min_dist
                add_vector_unit = np.array([x - p_x, y - p_y, z - p_z]) * min_dist / seg_length
                for i in range(int(num_inter_points)):
                    x_i, y_i, z_i = p_x + (i + 1) * add_vector_unit[0], p_y + (i + 1) * add_vector_unit[1], p_z + (
                    i + 1) * add_vector_unit[2]
                    point_list.append([len(point_list), x_i, y_i, z_i, direction_x, direction_y, direction_z])
        # add the current node
        point_list.append([len(point_list), x, y, z, direction_x, direction_y, direction_z])

    # recursively add the points in the child segments
    child_list = node.getChildren()
    # print('Number of children of current node:', len(child_list))
    for child in child_list:
        dfs_tree(child, point_list, node, min_dist)

    #print( len(point_list) )
    return point_list


def points_distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (
    z1 - z2) ** 2) ** 0.5  # do not calculate square root when unnecessary! May be too slow


def calculate_TP_FP_FN(point_list_EXT, point_list_GT, distance_thres, spacing):
    print("Extr_list: {}, Gt_list: {}".format(len(point_list_EXT), len(point_list_GT)))
    used_p_E_indices = np.zeros(len(point_list_EXT)).astype(bool)  # all False in the beginning
    num_TP = 0
    # record the numbers of 2 different types of false negatives
    num_FN_no_close_points = 0
    num_FN_wrong_direction = 0
    TPs = []
    GT_Fs = []

    cube_radius = math.sqrt(distance_thres**2 + (spacing/2)**2)  
    for p_G in point_list_GT:
        closest_p_E = None  # to store the closest point in EXT to p_G
        closest_p_E_distance_squared = math.inf
        id_G, x_G, y_G, z_G, dir_x_G, dir_y_G, dir_z_G = p_G

        # record the reason of a FN (if it is a FN)
        if_FN_no_close_points = True

        # to ensure that a corresponding point will be found, as long as the distance to the line <= distance_thres
        neighborhood_EXT = point_list_EXT[
            (point_list_EXT[:, 1] >= x_G - cube_radius) * (point_list_EXT[:, 1] <= x_G + cube_radius) *
            (point_list_EXT[:, 2] >= y_G - cube_radius) * (point_list_EXT[:, 2] <= y_G + cube_radius) *
            (point_list_EXT[:, 3] >= z_G - cube_radius) * (point_list_EXT[:, 3] <= z_G + cube_radius) *
            (1 - used_p_E_indices).astype(bool)]  # exclude points that are already used
        # print('p_G:', p_G)
        # print('neighborhood_EXT:', neighborhood_EXT)
        for p_E in neighborhood_EXT:
            id_E, x_E, y_E, z_E, dir_x_E, dir_y_E, dir_z_E = p_E
            # the distance from p_G to the line that goes through p_E
            E_G_distance_squared = point_distance_to_line_segment_squared((x_G, y_G, z_G), (x_E, y_E, z_E),
                                                                          (dir_x_E, dir_y_E, dir_z_E), spacing)
            if E_G_distance_squared <= distance_thres**2:  # if the distance is within threshold
            # This ensures that any line with a distance larger than distance_thres will be excluded
                if_FN_no_close_points = False
                if np.dot((dir_x_G, dir_y_G, dir_z_G),
                          (dir_x_E, dir_y_E, dir_z_E)) >= 0:  # directions are not so different
                    if (closest_p_E is None) or (E_G_distance_squared < closest_p_E_distance_squared):
                        closest_p_E = p_E
                        closest_p_E_distance_squared = E_G_distance_squared
        # print('closest_p_E:', closest_p_E)
        if closest_p_E is not None:
            used_p_E_indices[closest_p_E[0]] = True  # each point in EXT can correspond to at most 1 point in GT
            num_TP += 1
            TPs.append( (closest_p_E[1], closest_p_E[2], closest_p_E[3]) )
        else:  # if P_G has no corresponding point in graph E (false negative), record the reason why
            if if_FN_no_close_points:  # the reason is there's no close point to P_G
                num_FN_no_close_points += 1
            else:  # the reason is the close point to P_G has wrong direction
                num_FN_wrong_direction += 1
            GT_Fs.append( (x_G, y_G, z_G) )

    num_FP = point_list_EXT.shape[0] - used_p_E_indices.astype(int).sum()
    num_FN = point_list_GT.shape[0] - used_p_E_indices.astype(int).sum()

    # print('TP, FP, FN:', num_TP, num_FP, num_FN)
    # print('used_p_E_indices:', used_p_E_indices)
    return num_TP, num_FP, num_FN, num_FN_no_close_points, num_FN_wrong_direction, TPs, GT_Fs

def vector_dot_product(v0, v1):
    v0_x, v0_y, v0_z = v0
    v1_x, v1_y, v1_z = v1
    return v0_x*v1_x + v0_y*v1_y + v0_z*v1_z

def point_distance_to_line_segment_squared(point0, point1, dir1, spacing):
    """Calculate the distance from point0 to a line segment between point1 and its parent point, 
       the direction of the point1_parent to point1 is indicated with a vector dir1"""
       
    x0, y0 ,z0 = point0
    x1, y1 ,z1 = point1
    dir1_x, dir1_y, dir1_z = dir1

    dir1_len_squared = (dir1_x**2 + dir1_y**2 + dir1_z**2)
    # print('dir1_len_squared:', dir1_len_squared)
    
    vec10 = (x0-x1, y0-y1, z0-z1)
    vec10_len_squared = (vec10[0]**2 + vec10[1]**2 + vec10[2]**2)
    # print('vec10_len:', vec10_len)
    
    dot_vec10_dir1 = vector_dot_product(vec10, dir1)
    # print('dot_vec10_dir1:', dot_vec10_dir1)
    
    if vec10_len_squared == 0:  # check special cases first
        # print(1)
        distance_squared = 0
    elif dir1_len_squared == 0:  # use the point-point distance in this case
        # print(2)
        distance_squared = vec10_len_squared
    elif dot_vec10_dir1 >= 0:  # in this case, the parent point of point1 is even further from point0
        # print(3)
        distance_squared = vec10_len_squared  # use the point0-point1 distance in this case
    else:  # in this case, the parent point of point1 can be closer to point0
        # print(4)
        cos_angle_squared = dot_vec10_dir1**2 / (dir1_len_squared * vec10_len_squared)
        # sometimes cos_angle_squared becomes slightly larger than 1, because of the calculation accuracy
        # confine it within 1
        cos_angle_squared = min(1, cos_angle_squared)

        projection_on_line_squared = cos_angle_squared * vec10_len_squared
        if projection_on_line_squared >= spacing**2:
            # in this case, parent of point1 is the closest point of the line segment to point0
            # but in this case the parent point is also a candidate point in the neighborhood, so just use point1
            distance_squared = vec10_len_squared
        else:
            # in this case, the closest point of the line segment to point0 is between point1 and its parent point
            distance_squared = (1 - cos_angle_squared) * vec10_len_squared

    return distance_squared


def calculate_precision(TP, FP):
    precision = TP / (TP + FP)
    print('Precision:', precision)
    return precision


def calculate_recall(TP, FN):
    recall = TP / (TP + FN)
    print('Recall:', recall)
    return recall


def calculate_F1(TP, FP, FN):
    precision = calculate_precision(TP, FP)
    recall = calculate_recall(TP, FN)
    f1 = 2 * precision * recall / (precision + recall)
    print('F1 score:', f1)
    return f1, precision, recall


def evaluate_extraction(point_list_EXT, point_list_GT, distance_thres, spacing):
    point_list_EXT = np.array(point_list_EXT)
    point_list_GT = np.array(point_list_GT)
    TP, FP, FN, num_FN_no_close_points, num_FN_wrong_direction, TPs, GT_Fs = calculate_TP_FP_FN(point_list_EXT, point_list_GT, distance_thres, spacing)
    #print("\n\n{}\n".format(TPs))
    print('TP, FP, FN:', TP, FP, FN)
    print('num_FN_no_close_points, num_FN_wrong_direction:', num_FN_no_close_points, num_FN_wrong_direction)
    f1, pre, rec = calculate_F1(TP, FP, FN)
    return f1, pre, rec, TPs, GT_Fs


def evalGraph( inp, gt, distance_thres, spacing ):
    try:
        root_point_list_extracted = dfs_tree(inp.getRoot(), [], None, min_dist=spacing)
        root_point_list_extracted = np.array(root_point_list_extracted).astype(int)
        # print(root_point_list_extracted.astype(int).tolist()[:20])

        root_point_list_gt = dfs_tree(gt.getRoot(), [], None, min_dist=spacing)
        root_point_list_gt = np.array(root_point_list_gt).astype(int)
        # print(root_point_list_gt.astype(int).tolist()[:20])
        
        f1, pre, rec, TPs = evaluate_extraction(root_point_list_extracted, root_point_list_gt, distance_thres, spacing)
    except:
        f1, pre, rec = (0,0,0)
    print( "{}: Prec: {}, Rec: {}".format( f1, pre, rec ) )
