# -*- coding: utf-8 -*- 
import sys
import math
import numpy as np
import pdb

from odbAccess import *
from find_nearest_p import *

__all__ = ['slip_angle_extraction', 'slip_distance_extraction']   

def load_step(odb, step_name):
    try:
        step = odb.steps[step_name]
    except KeyError:
        print("Error: No step named", step_name)
        odb.close()
        sys.exit()
    return step

def slip_angle_extraction(odb_name, instance_name):
    print("...Slip Extraction...")
    
    try:
        odb = openOdb(path=odb_name, readOnly=True)
    except OdbError as e:
        print("No ODB")
        exit()

    step_subrotation = odb.steps['subrotation'] 

    L1_name = 'L1'
    L1_node_set = odb.rootAssembly.nodeSets[L1_name]

    L1_node_label = L1_node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    L1_node_name = 'Node ASSEMBLY.{}'.format(L1_node_label)
    
    try:
        history_region_subrotation = step_subrotation.historyRegions[L1_node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.4' not found in odb file: {}".format(odb_name))
        
    L1_U3_subrot = history_region_subrotation.historyOutputs['U3'].data  # 'U2' 기입
    
    
    velocity_of_subrot = 4.63*2
    
    L1_U3_subrot_list = []
    subrot_ori_dist_list = []
    subrot_gap_list = []
    time_list =[]
    prev_subrot_gap = None
    
    for time, value in L1_U3_subrot:
        L1_U3_subrot_list.append(value)
        time_list.append(time)
        
        subrot_original_distance = velocity_of_subrot * time
        subrot_ori_dist_list.append(subrot_original_distance)
        # subrot_gap = math.degrees(abs(value/30 - subrot_original_distance))
        subrot_gap = abs(value - subrot_original_distance*30)
        subrot_gap_list.append(subrot_gap)

        if prev_subrot_gap is not None and subrot_gap < prev_subrot_gap:
            break

        prev_subrot_gap = subrot_gap
    
    print("Subrotation gap: ", subrot_gap_list)
        
    max_angle_difference = max(subrot_gap_list)
    max_angle_index = subrot_gap_list.index(max_angle_difference)
    subrot_stop_time = time_list[max_angle_index]
    print("Max angle difference: {} at frame {}".format(max_angle_difference, max_angle_index))
    return max_angle_difference, subrot_stop_time, max_angle_index
    
    
    
def slip_distance_extraction(odb_name, instance_name):
    print("...Slip Extraction...")
    
    try:
        odb = openOdb(path=odb_name, readOnly=True)
    except OdbError as e:
        print("No ODB")
        exit()

    step_rotation = odb.steps['rotation'] 

    tire_center_name = 'TIRE_CENTER_2'
    center_node_set = odb.rootAssembly.nodeSets[tire_center_name]

    center_node_label = center_node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    center_name = 'Node ASSEMBLY.{}'.format(center_node_label)
    
    try:
        history_region_rotation= step_rotation.historyRegions[center_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.4' not found in odb file: {}".format(odb_name))
        
    tire_u3_rot = history_region_rotation.historyOutputs['U1'].data  # 'U2' 기입

    
    velocity_of_rot = 5.56*2
    
    
    
    center_U1_rot_list = []
    rot_ori_distance_list = []
    rot_gap_list = []
    rot_time_list =[]
    prev_rot_gap = None
    
    for idx, (time, value) in enumerate(tire_u3_rot):
        center_U1_rot_list.append(value)
        rot_time_list.append(time)
        
        rot_original_distance = velocity_of_rot * time * 150
        rot_ori_distance_list.append(rot_original_distance)
        rot_gap = abs(value - rot_original_distance)
        rot_gap_list.append(rot_gap)

        if prev_rot_gap is not None and rot_gap < prev_rot_gap:
            break

        prev_rot_gap = rot_gap
    
    max_dist_difference = max(rot_gap_list)
    max_dist_index = rot_gap_list.index(max_dist_difference)    
    rot_stop_time = rot_time_list[max_dist_index]
    
    print("Max slip distance difference: {} at frame {}".format(max_dist_difference, max_dist_index))
    
    return max_dist_difference, rot_stop_time, max_dist_index
        
    
    
    
    