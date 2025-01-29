# -*- coding: utf-8 -*- 
import os
import csv
import pdb

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
    
    time_graph = [] 
    displacement_graph = []
    for time, displacement in displacement_history_U_subrotation:
        time_graph.append(time)
        displacement_graph.append(displacement)
        
    for time, displacement in displacement_history_U_rotation:
        time_graph.append(time)
        displacement_graph.append(displacement)
        pdb.set_trace()
        
    