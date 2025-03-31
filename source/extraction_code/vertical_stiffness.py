# -*- coding: utf-8 -*- 
import os
import csv
import pdb
from odbAccess import *

__all__ = ['vertical_stiffness_extraction'] 

def vertical_stiffness_extraction(odb_name, instance_name, graph_plot=False):
    print("...Vertical Stiffness Extraction...")
    
    time_graph_loading = []
    time_graph_loading_300 = []
    displacement_loading_graph = []
    displacement_loading_300_graph = []
    force_loading_graph = []
    force_graph = []
    stiffness_graph = []

    # temp
    displacement_diff_graph = []
    force_diff_graph = []
    
    # Open the odb file
    odb = openOdb(path=odb_name)
    step_loading = odb.steps['loading'] 
    step_loading_300 = odb.steps['loading_300N'] 
    
    supporter_name = 'SUPPORTER_CENTER'
    supporter_node_set = odb.rootAssembly.nodeSets[supporter_name]

    assembly_node_label = supporter_node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    node_name = 'Node ASSEMBLY.{}'.format(assembly_node_label)
    
    try:
        history_region_loading = step_loading.historyRegions[node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.4' not found in odb file: {}".format(odb_name))
        
    displacement_history_U_loading = history_region_loading.historyOutputs['U2'].data  # 'U2' 기입
    
    # Extract displacement data (U2 in this case)
    force_history_loading = history_region_loading.historyOutputs['RF2'].data  # 'U2' 기입
    
    idx = 0
    for time, force_loading in force_history_loading:
        time_graph_loading.append(time)
        force_loading_graph.append(force_loading)
        displacement_loading_graph.append(displacement_history_U_loading[idx][1])
        idx += 1
        
    for idx in range(len(force_loading_graph) - 1, -1, -1):
        if abs(force_loading_graph[idx]) < 0.001:
            initial_u2 = displacement_loading_graph[idx]
            break
        
        
    try:
        history_region = step_loading_300.historyRegions[node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.4' not found in odb file: {}".format(odb_name))
   
    # Extract displacement data (U2 in this case)
    displacement_history_U = history_region.historyOutputs['U2'].data  # 'U2' 기입
    for time, displacement_loading_300 in displacement_history_U:
        time_graph_loading_300.append(time)
        displacement_loading_300_graph.append(displacement_loading_300)
    odb.close()

    force_ori = 225
    # Force and Stiffness Calculation


    # for i in range(len(time_graph)):
    #     time = time_graph[i]
    #     force = force_ori * time  # 시간에 따라 선형 증가하는 힘
    #     force_graph.append(force)
    #     pdb.set_trace()
    #     if i > 0 :
    #         if (displacement_graph[i] - displacement_graph[i - 1]) < 0:
    #             # 이전 단계의 데이터와 현재 데이터를 이용하여 강성 계산
    #             displacement_diff = abs(displacement_graph[i] - displacement_graph[i - 1])
    #             force_diff = force_graph[i] - force_graph[i - 1]
                
    #             # temp
    #             displacement_diff_graph.append(displacement_diff)
    #             force_diff_graph.append(force_diff)
                
            
    #             stiffness = force_diff / displacement_diff if displacement_diff != 0 else 0
    #             stiffness_graph.append(stiffness)
        
    #     else:
    #         # stiffness_graph.append(0)  # 초기값
    #         pass

    # print(time_graph)
    # print(force_graph)
    # print(displacement_diff_graph)
    # print(force_diff_graph)
    # print(stiffness_graph)
    # sttiffness_sum = 0
    # for i in range(len(stiffness_graph)):
    #     sttiffness_sum += stiffness_graph[i]
    
        
    # average_stiffness = sttiffness_sum / (len(stiffness_graph))

    
    # last_frame_timestep = time_graph[-1] - time_graph[-2]
    displacement_gap = displacement_loading_300_graph[-1] - initial_u2

    last_frame_stiffness = abs(force_ori / displacement_gap)  

    # initial_frame_stiffness = stiffness_graph[0]
    # print("Avg Vertical stiffness: {}\n".format(average_stiffness))
    # print("Last Frame Vertical stiffness: {}\n".format(last_frame_stiffness))
    # print("Initial Frame Vertical stiffness: {}\n".format(initial_frame_stiffness))
    print("Last Frame Vertical stiffness: {}\n".format(last_frame_stiffness))
    # print("Last Frame Vertical stiffness: {}\n".format(average_stiffness))
    
    # return average_stiffness, last_frame_stiffness, initial_frame_stiffness
    return last_frame_stiffness