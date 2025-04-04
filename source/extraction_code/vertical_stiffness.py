# -*- coding: utf-8 -*- 
import os
import csv
import pdb
from odbAccess import *
from find_nearest_p import find_node_with_min_y
__all__ = ['vertical_stiffness_extraction'] 

def vertical_stiffness_extraction(odb_name, instance_name, graph_plot=False):
    print("...Vertical Stiffness Extraction...")
    
    time_graph_loading = []
    time_graph_loading_300 = []
    displacement_loading_graph = []
    displacement_loading_300_graph = []
    tire_center_displacement_graph = []
    force_graph = []
    stiffness_graph = []

    # temp
    displacement_diff_graph = []
    force_diff_graph = []
        
    # Open the odb file
    odb = openOdb(path=odb_name)
    
    try:
        myInstance = odb.rootAssembly.instances[instance_name]
    except KeyError:
        print("Error: No instance")
        odb.close()
        exit()
        
    step_loading = odb.steps['loading'] 
    step_loading_300 = odb.steps['loading_300N'] 
    step_bending = odb.steps['bending']
    
    len_frames = len(step_bending.frames)
    last_frame = step_bending.frames[len_frames -1]
    
    displacement_field_last = last_frame.fieldOutputs['U'].getSubset(region=myInstance)

    displacement_values_last = {value.nodeLabel: value for value in displacement_field_last.values}

    # the node with the minimum Y coordinate in the last frame (Node A)
    min_y_node = find_node_with_min_y(myInstance.nodes, displacement_values_last)
    if min_y_node:
        node_a = min_y_node.label

    else:
        print("Error: Could not find node with minimum Y in last frame.")
        odb.close()
        exit()
        
    print("Node A: ", node_a)
        
    # inintial frame (index 0)
    for i in range(len(step_loading.frames)):
        frame_data = step_loading.frames[i]
        displacement_field = frame_data.fieldOutputs['U'].getSubset(region=myInstance)
        displacement_values = {value.nodeLabel: value for value in displacement_field.values}
        node_a_disp = displacement_values.get(node_a)
        
        node_a_coord_x = min_y_node.coordinates[0] + node_a_disp.data[0]
        node_a_coord_y = min_y_node.coordinates[1] + node_a_disp.data[1]
        node_a_coord_z = min_y_node.coordinates[2] + node_a_disp.data[2]
        
        if node_a_coord_y < -79.99:
            inintial_time = frame_data.frameValue
            inintial_frame = frame_data
            break
    
    
    supporter_name = 'TIRE_CENTER_2'
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
    for time, tire_center_displacement in displacement_history_U_loading:
        time_graph_loading.append(time)
        tire_center_displacement_graph.append(tire_center_displacement)
        
        if round(time, 4) == round(inintial_time, 4):
            initial_u2 = tire_center_displacement_graph[idx]
            # print("Initial U2: ", initial_u2)
            break
        else:
            idx += 1
            
            
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