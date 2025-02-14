# -*- coding: utf-8 -*- 
import os
import csv

from odbAccess import *

__all__ = ['vertical_stiffness_extraction'] 

def vertical_stiffness_extraction(odb_name, instance_name, graph_plot=False):
    print("...Vertical Stiffness Extraction...")
    
    time_graph = []
    displacement_graph = []
    force_graph = []
    stiffness_graph = []

    # temp
    displacement_diff_graph = []
    force_diff_graph = []
    
    # Open the odb file
    odb = openOdb(path=odb_name)
    step = odb.steps['loading_300N'] 
    # step = odb.steps['loading'] 
    
    # node_set_name = 'TIRE_CENTER_2'
    node_set_name = 'SUPPORTER_CENTER'

    node_set = odb.rootAssembly.nodeSets[node_set_name]
    
    assembly_node_label = node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    node_name = 'Node ASSEMBLY.{}'.format(assembly_node_label)

    try:
        history_region = step.historyRegions[node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.4' not found in odb file: {}".format(odb_name))
   
    # Extract displacement data (U2 in this case)
    displacement_history_U = history_region.historyOutputs['U2'].data  # 'U2' 기입
    for time, displacement in displacement_history_U:
        time_graph.append(time)
        displacement_graph.append(displacement)
    odb.close()

    print(displacement_history_U)
    displacement_last_frame = displacement_graph[-1]

    return displacement_last_frame 