# -*- coding: utf-8 -*- 
import numpy as np
import os
import csv
from odbAccess import *

__all__ = ['tire_center_displacement_extraction']

def tire_center_displacement_extraction(odb_name):
    print("...Tire Center Displacement Extraction...")


    # Open the odb file
    odb = openOdb(path=odb_name)
    step_subrotation = odb.steps['subrotation'] 
    step_rotation = odb.steps['rotation'] 
    
    node_set_name = 'TIRE_CENTER_2'
    node_set = odb.rootAssembly.nodeSets[node_set_name]
    
    assembly_node_label = node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    node_name = 'Node ASSEMBLY.{}'.format(assembly_node_label)
    
    try:
        history_region_subrotation = step_subrotation.historyRegions[node_name]  # Node PartName.nodenum
        history_region_rotation = step_rotation.historyRegions[node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.4' not found in odb file: {}".format(odb_name))
   
    # Extract displacement data (U2 in this case)
    displacement_history_U_subrotation = history_region_subrotation.historyOutputs['U2'].data  
    displacement_history_U_rotation = history_region_rotation.historyOutputs['U2'].data 
    
    time_graph_total = []
    time_graph_subrot = [] 
    displacement_graph_subrot = []
    velocity_graph = []
    prev_time = None
    prev_disp = None
    
    displcaement_graph_total = []
    
    
    for time_subrot, displacement_subrot in displacement_history_U_subrotation:
        time_graph_subrot.append(time_subrot)
        displacement_graph_subrot.append(displacement_subrot)
        displcaement_graph_total.append(displacement_subrot)
        time_graph_total.append(time_subrot)
        if prev_time is not None and prev_disp is not None:
            velocity = (displacement_subrot - prev_disp) / (time_subrot - prev_time)
            velocity_graph.append(velocity)
            
        else:
            velocity_graph.append(0)
            
        prev_time = time_subrot
        prev_disp = displacement_subrot
        
    
    time_rot_start = time_graph_subrot[-1]
    time_graph_rot =[]
    displacement_graph_rot = []
    prve_time = None
    prev_disp = None
    
    for time_rot, displacement_rot in displacement_history_U_rotation:
        
        if time_rot > 0.0762:
            break
        time_graph_rot.append(time_rot)
        time_graph_total.append(time_rot + time_rot_start)
        displacement_graph_rot.append(displacement_rot)
        displcaement_graph_total.append(displacement_rot)
        
        if prev_time is not None and prev_disp is not None:
            velocity = (displacement_rot - prev_disp) / (time_rot - prev_time)
            velocity_graph.append(velocity)
        else:
            velocity_graph.append(0)
        
        prev_time = time_rot
        prev_disp = displacement_rot
        
    max_disp_subrot = max(displacement_graph_subrot)
    min_disp_subrot = min(displacement_graph_subrot)
    subrot_gap = abs(max_disp_subrot - min_disp_subrot)
    
    max_disp_rot = max(displacement_graph_rot)
    min_disp_rot = min(displacement_graph_rot)
    rot_gap = abs(max_disp_rot - min_disp_rot)
    
    max_disp_total = max(displcaement_graph_total)
    min_disp_total = min(displcaement_graph_total)
    total_gap = abs(max_disp_total - min_disp_total)
    
    total_std = np.std(displcaement_graph_total)
    
    
    # CSV output file
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    csv_path_name = os.path.join('results','Tire_center', csv_file_name)
    
    with open(csv_path_name, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(['Time', 'Total Displacement', 'Velocity'])
        for i in range(len(velocity_graph)):
            writer.writerow([time_graph_total[i], displcaement_graph_total[i], velocity_graph[i]])
    
    return subrot_gap, rot_gap, total_gap, total_std, velocity_graph
    