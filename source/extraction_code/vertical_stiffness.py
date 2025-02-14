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

    force_ori = 150
    # Force and Stiffness Calculation


    for i in range(len(time_graph)):
        time = time_graph[i]
        force = force_ori * time  # 시간에 따라 선형 증가하는 힘
        force_graph.append(force)
        if i > 0 :
            if (displacement_graph[i] - displacement_graph[i - 1]) < 0:
                # 이전 단계의 데이터와 현재 데이터를 이용하여 강성 계산
                displacement_diff = abs(displacement_graph[i] - displacement_graph[i - 1])
                force_diff = force_graph[i] - force_graph[i - 1]
                
                # temp
                displacement_diff_graph.append(displacement_diff)
                force_diff_graph.append(force_diff)
                
            
                stiffness = force_diff / displacement_diff if displacement_diff != 0 else 0
                stiffness_graph.append(stiffness)
        
        else:
            # stiffness_graph.append(0)  # 초기값
            pass

    # print(time_graph)
    # print(force_graph)
    # print(displacement_diff_graph)
    # print(force_diff_graph)
    # print(stiffness_graph)
    sttiffness_sum = 0
    for i in range(len(stiffness_graph)):
        sttiffness_sum += stiffness_graph[i]
        
        
    average_stiffness = sttiffness_sum / (len(stiffness_graph))

    
    last_frame_timestep = time_graph[-1] - time_graph[-2]
    last_frame_displacement = displacement_graph[-1] - displacement_graph[-2]

    last_frame_stiffness = force_ori*last_frame_timestep / last_frame_displacement  



    initial_frame_stiffness = stiffness_graph[0]
    # print("Avg Vertical stiffness: {}\n".format(average_stiffness))
    # print("Last Frame Vertical stiffness: {}\n".format(last_frame_stiffness))
    # print("Initial Frame Vertical stiffness: {}\n".format(initial_frame_stiffness))
    print("Last Frame Vertical stiffness: {}\n".format(last_frame_stiffness))
    # print("Last Frame Vertical stiffness: {}\n".format(average_stiffness))
    
    # return average_stiffness, last_frame_stiffness, initial_frame_stiffness
    return last_frame_stiffness