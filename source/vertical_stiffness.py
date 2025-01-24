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

    # Open the odb file
    odb = openOdb(path=odb_name)
    step = odb.steps['loading_300N'] 
    # step = odb.steps['loading'] 
    
    node_set_name = 'TIRE_CENTER_2'
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

    force_ori = 150
    # Force and Stiffness Calculation
    for i in range(len(time_graph)):
        time = time_graph[i]
        force = force_ori * time  # 시간에 따라 선형 증가하는 힘
        force_graph.append(force)
        if i > 0:
            # 이전 단계의 데이터와 현재 데이터를 이용하여 강성 계산
            displacement_diff =(displacement_graph[i] - displacement_graph[i - 1])
            force_diff = force_graph[i] - force_graph[i - 1]
            stiffness = force_diff / displacement_diff if displacement_diff != 0 else 0
            stiffness_graph.append(stiffness)
        else:
            stiffness_graph.append(0)  # 초기값

    average_stiffness=force_ori/(displacement_graph[0]-displacement_graph[i]) #최종 강성

    print("Avg Vertical stiffness: {}\n".format(average_stiffness))
    
    return average_stiffness