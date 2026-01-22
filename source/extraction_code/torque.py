# -*- coding: utf-8 -*- 
import os
import csv
import sys
import numpy as np
import pdb
from odbAccess import *

__all__ = ['torque_extraction']

def torque_extraction(odb_name):
    print("...Torque Extraction...")
    odb = openOdb(path=odb_name, readOnly=True)
    step = odb.steps['subrotation']
    
    element_set_name = 'WIRE-2-SET-1'
    element_set = odb.rootAssembly.elementSets[element_set_name]
    assembly_element_label = element_set.elements[0][0].label
    element_name = 'Element ASSEMBLY.{}'.format(assembly_element_label)
    
    try:
        history_region = step.historyRegions[element_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Element ASSEMBLY.2' not found in odb file: {}".format(odb_name))    
        
    CTM1 = history_region.historyOutputs['CTM1'].data
    CTM2 = history_region.historyOutputs['CTM2'].data
    torque_x = np.array(CTM1)
    torque_y = np.array(CTM2)

    time = torque_x[:,0]
    torque_magnitude = np.sqrt(torque_x[:,1]**2 + torque_y[:,1]**2)
    torque = np.column_stack((time, torque_magnitude))
    
    torque_last_frame = torque[-1,1]
    print("Torque at last frame: {}".format(torque_last_frame))

    max_torque = np.max(torque_magnitude)
    print("Max Torque: {}\n".format(max_torque))

    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    results_dir = os.path.join('results', 'Torque')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    csv_path_name = os.path.join(results_dir, csv_file_name)

    headers = ["Time", "Torque"]

    if sys.version_info[0] < 3:
        mode = 'wb'
        kwargs = {}
    else:
        mode = 'w'
        kwargs = {'newline': ''}

    with open(csv_path_name, mode, **kwargs) as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(torque)
        
        
    step2 = odb.steps['rotation']
    
    element_set_name2 = 'TIRE_CENTER_2'
    element_set2 = odb.rootAssembly.nodeSets[element_set_name2]
    assembly_element_label2 = element_set2.nodes[0][0].label
    element_name2 = 'Node ASSEMBLY.{}'.format(assembly_element_label2)
    
    
    try:
        history_region2 = step2.historyRegions[element_name2]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Element ASSEMBLY.2' not found in odb file: {}".format(odb_name))  
    RM3 = history_region2.historyOutputs['RM3'].data
    
    RM3_list = []
    for i in range(len(RM3)):
        if RM3[i][0] > 0.04:
            break
        RM3_list.append(abs(RM3[i][1]))
        
    torque_2 = np.array(RM3_list)

    max_torque2 = np.max(torque_2)
    print("Max Torque2: {}\n".format(max_torque2))

    # --- New Extraction Logic: Separate Folders for L1_U3 and Tire_U1 ---
    try:
        # 1. Extract L1 U3 from subrotation and save to results/slip_angle
        slip_angle_dir = os.path.join('results', 'slip_angle')
        if not os.path.exists(slip_angle_dir):
            os.makedirs(slip_angle_dir)
            
        csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
        l1_csv_path = os.path.join(slip_angle_dir, csv_file_name)
        
        try:
            L1_name = 'L1'
            L1_node_set = odb.rootAssembly.nodeSets[L1_name]
            L1_node_label = L1_node_set.nodes[0][0].label
            L1_node_name = 'Node ASSEMBLY.{}'.format(L1_node_label)
            
            hr_subrot = step.historyRegions[L1_node_name]
            L1_U3_data = hr_subrot.historyOutputs['U3'].data
            
            if sys.version_info[0] < 3:
                mode = 'wb'
                kwargs = {}
            else:
                mode = 'w'
                kwargs = {'newline': ''}

            with open(l1_csv_path, mode, **kwargs) as f:
                writer = csv.writer(f)
                writer.writerow(['Time', 'L1_U3'])
                writer.writerows(L1_U3_data)
            # print("Saved L1_U3 data to {}".format(l1_csv_path))
                
        except Exception as e:
            print("Error extracting/saving L1 U3: {}".format(e))

        # 2. Extract Tire Center U1 from rotation and save to results/slip_dist
        slip_dist_dir = os.path.join('results', 'slip_dist')
        if not os.path.exists(slip_dist_dir):
            os.makedirs(slip_dist_dir)
            
        tire_csv_path = os.path.join(slip_dist_dir, csv_file_name)

        try:
            tire_center_name = 'TIRE_CENTER_2'
            center_node_set = odb.rootAssembly.nodeSets[tire_center_name]
            center_node_label = center_node_set.nodes[0][0].label
            center_name = 'Node ASSEMBLY.{}'.format(center_node_label)
            
            hr_rot = step2.historyRegions[center_name]
            tire_u1_data = hr_rot.historyOutputs['U1'].data
            
            if sys.version_info[0] < 3:
                mode = 'wb'
                kwargs = {}
            else:
                mode = 'w'
                kwargs = {'newline': ''}
                
            with open(tire_csv_path, mode, **kwargs) as f:
                writer = csv.writer(f)
                writer.writerow(['Time', 'Tire_U1'])
                writer.writerows(tire_u1_data)
            # print("Saved Tire_U1 data to {}".format(tire_csv_path))
            
        except Exception as e:
            print("Error extracting/saving Tire Center U1: {}".format(e))
            
    except Exception as e:
        print("Error in separate slip data extraction: {}".format(e))
    # --------------------------------------------------------------------

    return torque_last_frame, max_torque, max_torque2