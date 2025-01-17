# -*- coding: utf-8 -*- 
from odbAccess import *
import math
import sys
from find_nearest_p import *
# from get_slip_dist import *
import re
import csv
import os
import numpy as np
import matplotlib.pyplot as plt


def slip_angle_dist_extraction(odb_name, instance_name):
    print("...Slip Angle and Distance Extraction...")
    try:
        odb = openOdb(path=odb_name, readOnly=True)
    except OdbError as e:
        print("No ODB")
        exit()


    try:
        step_bending = odb.steps['bending']
    except KeyError:
        print("Error: No bending")
        odb.close()
        exit()

    len_frames = len(step_bending.frames)

    try:
        step_subrotation = odb.steps['subrotation']
    except KeyError:
        print("Error: No subrotation")
        odb.close()
        sys.exit()

    len_frames_subrotation = len(step_subrotation.frames)

    try:
        step_rotation = odb.steps['rotation']
    except KeyError:
        print("Error: No subrotation")
        odb.close()
        sys.exit()

    len_frames_rotation = len(step_rotation.frames)


    try:
        myInstance = odb.rootAssembly.instances[instance_name]
    except KeyError:
        print("Error: No instance")
        odb.close()
        exit()

    # count the number of nodes in the instance

    # last frame (index len_frames - 1)
    last_frame = step_bending.frames[len_frames -1]
    displacement_field_last = last_frame.fieldOutputs['U'].getSubset(region=myInstance)

    displacement_values_last = {value.nodeLabel: value for value in displacement_field_last.values}

    # the node with the minimum Y coordinate in the last frame (Node A)
    min_y_node = find_node_with_min_y(myInstance.nodes, displacement_values_last)
    if min_y_node:
        node_a = min_y_node.label
        # node_a_x = min_y_node.coordinates[0] + displacement_values_last[node_a].data[0]
        # node_a_y = min_y_node.coordinates[1] + displacement_values_last[node_a].data[1]
        # node_a_z = min_y_node.coordinates[2] + displacement_values_last[node_a].data[2]

    else:
        print("Error: Could not find node with minimum Y in last frame.")
        odb.close()
        exit()

    # inintial frame (index 0)
    initial_frame = step_bending.frames[0]
    displacement_field_initial = initial_frame.fieldOutputs['U'].getSubset(region=myInstance)
    displacement_values_initial = {value.nodeLabel: value for value in displacement_field_initial.values}

    node_a_initial_disp = displacement_values_initial.get(node_a)
    if node_a_initial_disp is None:
        print("Error: Initial frame displacement not found for Node A.")
        odb.close()
        sys.exit()

    try:
        node_a_initial_x = min_y_node.coordinates[0] + node_a_initial_disp.data[0]
        node_a_initial_y = min_y_node.coordinates[1] + node_a_initial_disp.data[1]
        node_a_initial_z = min_y_node.coordinates[2] + node_a_initial_disp.data[2]
        
    except OdbError:
        node_a_initial_x = min_y_node.coordinates[0] + node_a_initial_disp.dataDouble[0]
        node_a_initial_y = min_y_node.coordinates[1] + node_a_initial_disp.dataDouble[1]
        node_a_initial_z = min_y_node.coordinates[2] + node_a_initial_disp.dataDouble[2]

    # target point in the initial frame
    target_point = (node_a_initial_x, node_a_initial_y + 30 , node_a_initial_z)

    # the node closest to the target point in the initial frame (Node B)
    closest_node = find_closest_node(target_point, myInstance.nodes, displacement_values_initial)
    if closest_node:
        node_b = closest_node.label
        node_b_info = closest_node
        # node_b_x = closest_node.coordinates[0] + displacement_values_initial[node_b].data[0]
        # node_b_y = closest_node.coordinates[1] + displacement_values_initial[node_b].data[1]
        # node_b_z = closest_node.coordinates[2] + displacement_values_initial[node_b].data[2]

    
    else:
        print("Error: Could not find a node closest to the target point in initial frame.")

    # the node with the minimum Y coordinate among the nodes with the minimum X coordinate in the initial frame (Node C)
    min_x_nodes = find_nodes_with_min_x(myInstance.nodes, displacement_values_initial)


    if min_x_nodes:
        min_y_among_min_x_node = find_node_with_min_y_among(min_x_nodes, displacement_values_initial)
        if min_y_among_min_x_node:
            node_c = min_y_among_min_x_node.label
            
            try:
                node_c_x = min_y_among_min_x_node.coordinates[0] + displacement_values_initial[node_c].data[0]
                node_c_y = min_y_among_min_x_node.coordinates[1] + displacement_values_initial[node_c].data[1]
                node_c_z = min_y_among_min_x_node.coordinates[2] + displacement_values_initial[node_c].data[2]
                
            except OdbError:
                node_c_x = min_y_among_min_x_node.coordinates[0] + displacement_values_initial[node_c].dataDouble[0]
                node_c_y = min_y_among_min_x_node.coordinates[1] + displacement_values_initial[node_c].dataDouble[1]
                node_c_z = min_y_among_min_x_node.coordinates[2] + displacement_values_initial[node_c].dataDouble[2]

        
        else:
            print("Error: Could not find node with min Y among nodes with min X in initial frame.")
    else:
        print("Error: No nodes found with min X in initial frame.")
        
    target_point_e = (node_c_x, node_c_y + 30 , node_c_z)
    # print(target_point_e)
    closest_node_e = find_closest_node(target_point_e, myInstance.nodes, displacement_values_initial)
    if closest_node_e:
        node_e = closest_node_e.label
        
    else:
        print("Error: Could not find a node closest to the target point in initial frame.")

    # Get the last frame of the 'rotation' step
    last_frame_subrotation = step_subrotation.frames[-1]

    # Get the displacement field output for the specific instance
    displacement_field_last_subrotation = last_frame_subrotation.fieldOutputs['U'].getSubset(region=myInstance)

    # Create a dictionary mapping node labels to displacement values for the instance
    displacement_values_last_subrotation = {value.nodeLabel: value for value in displacement_field_last_subrotation.values}

    # Now, proceed with finding the node with minimum Y coordinate
    # min_y_node_D = find_node_with_min_y(myInstance.nodes, displacement_values_last_subrotation)
    min_y_node_D = find_closest_node_to_target(myInstance.nodes, node_b_info, displacement_values_last_subrotation)

    if min_y_node_D:
        node_d = min_y_node_D.label
        # node_d_x = min_y_node_D.coordinates[0] + displacement_values_last_subrotation[node_d].data[0]
        # node_d_y = min_y_node_D.coordinates[1] + displacement_values_last_subrotation[node_d].data[1]
        # node_d_z = min_y_node_D.coordinates[2] + displacement_values_last_subrotation[node_d].data[2]
        

    ## Print the nodes for verification
    # print("Last frame: Node with min Y (Node A): {}".format(node_a))
    # print("Initial frame: Node closest to target point (Node B): {}".format(node_b))
    # print("Initial frame: Node with min Y among nodes with min X (Node C): {}".format(node_c))
    # print("Last frame of 'rotation' step: Node with min Y (Node D): {}".format(node_d))
    # print("node e: {}\n".format(node_e))


    # Get the angle difference between noce A, B
    angleslist_ba = get_angle_per_frame(odb, step_subrotation, myInstance, node_a, node_b, node_a)
    # Get the angle difference between noce C, E
    angelslist_ec = get_angle_per_frame(odb, step_subrotation, myInstance, node_c, node_e, node_a)
    
    angle_differences = [abs(a[1] - b[1]) for a, b in zip(angleslist_ba, angelslist_ec)]
    # print(angle_differences)
    max_angle_difference = max(angle_differences)
    max_index = angle_differences.index(max_angle_difference)
    
    print("Max angle difference: {} at frame {}".format(max_angle_difference, max_index))
    
    if len(step_rotation.frames) == 0:
        max_slip_distance = 'No Rotation Step'
        idx = 'No Rotation Step'
    else:
        max_slip_distance, _, idx = get_slip_dist(odb, step_rotation, myInstance, node_d, node_b)

    print("Max distance gap: {} at frame {}\n".format(max_slip_distance, idx))
    
    return max_angle_difference, max_slip_distance

def get_slip_dist(odb, step, myInstance, node_1, node_2):
    """Calculate the slip distance between two nodes in 3D space in ROTATION Step."""
    
    center2= odb.rootAssembly.nodeSets['TIRE_CENTER_2']

    len_frames = len(step.frames)
    first_frame = step.frames[0]
    first_displacement_field = first_frame.fieldOutputs['U'].getSubset(region=myInstance)
    first_displacement_values = {value.nodeLabel: value for value in first_displacement_field.values}

    node_1_initial_disp = first_displacement_values.get(node_1)
    node_2_initial_disp = first_displacement_values.get(node_2)
    if node_1_initial_disp is None or node_2_initial_disp is None:
        print("Error: Initial displacement not found for Node A or Node C in subrotation step.")
        odb.close()
        sys.exit()
        
    # Get initial displacement for center2 node
    first_displacement_field_center2 = first_frame.fieldOutputs['U'].getSubset(region=center2)
    
    if not first_displacement_field_center2.values:
        print("Error: Initial displacement not found for Center 2 node in subrotation step.")
        odb.close()
        sys.exit()

    try: 
        center2_initial_disp = first_displacement_field_center2.values[0].data
    except OdbError:
        center2_initial_disp = first_displacement_field_center2.values[0].dataDouble
    
    # Retrieve nodes from the center2 node set
    center2_nodes = center2.nodes
    # Assuming there's only one node in center2
    center2_node = center2_nodes[0][0]
    center2_initial_coords = [coord + disp for coord, disp in zip(center2_node.coordinates, center2_initial_disp)]
    
    ## Calculate the vectors of nodes for the initial frame
    try:
        initial_node_1_disp = node_1_initial_disp.data
    except OdbError:
        initial_node_1_disp = node_1_initial_disp.dataDouble
        
    initial_node_1 = [myInstance.nodes[node_1 - 1].coordinates[i] + initial_node_1_disp[i] for i in range(3)]
    
    try: 
        initial_node_2_disp = node_2_initial_disp.data
    except OdbError:
        initial_node_2_disp = node_2_initial_disp.dataDouble
        
    initial_node_2 = [myInstance.nodes[node_2 - 1].coordinates[i] + initial_node_2_disp[i] for i in range(3)]

    initial_vector_ba = [initial_node_1[i] - center2_initial_coords[i] for i in range(3)]
    initial_vector_ca = [initial_node_2[i] - center2_initial_coords[i] for i in range(3)]
    
    ## Calculate the vectors of nodes for each frame
    angle_differences = []
    contact_status = True
    for i in range(len_frames):
        frame = i
        new_frame = step.frames[i]
        new_displacement_field = new_frame.fieldOutputs['U'].getSubset(region=myInstance)
        new_displacement_values = {value.nodeLabel: value for value in new_displacement_field.values}
        

        # node 1 (Ground)
        try:
            current_node_1_disp = new_displacement_values[node_1].data
        except OdbError:
            current_node_1_disp = new_displacement_values[node_1].dataDouble
            
        current_node_1 = [myInstance.nodes[node_1 - 1].coordinates[i] + current_node_1_disp[i] for i in range(3)]

        # node 2 (air)
        try:
            current_node_2_disp = new_displacement_values[node_2].data
        except OdbError:
            current_node_2_disp = new_displacement_values[node_2].dataDouble
            
        current_node_2 = [myInstance.nodes[node_2 - 1].coordinates[i] + current_node_2_disp[i] for i in range(3)]
        
        # Center2 Node
        new_displacement_field_center2 = new_frame.fieldOutputs['U'].getSubset(region=center2)
        if not new_displacement_field_center2.values:
            print("Error: Displacement not found for Center 2 node at frame", i)
            continue
        
        try:
            center2_current_disp = new_displacement_field_center2.values[0].data
        except OdbError:
            center2_current_disp = new_displacement_field_center2.values[0].dataDouble
            
        center2_current_coords = [coord + disp for coord, disp in zip(center2_node.coordinates, center2_current_disp)]
  
        current_vector_ba = [current_node_1[i] - center2_current_coords[i] for i in range(3)]
        current_vector_ca = [current_node_2[i] - center2_current_coords[i] for i in range(3)]
        
        if current_node_1[1] > -79.0:
            contact_status = False
        else: 
            contact_status = True
            
             
        current_angle_ba = calculate_angle_between_vectors(current_vector_ba, initial_vector_ba)
        current_angle_ca = calculate_angle_between_vectors(current_vector_ca, initial_vector_ca)
        angle_difference = current_angle_ba - current_angle_ca
        angle_differences.append((frame, current_angle_ba, current_angle_ca, angle_difference))
        
        if contact_status == False:
            current_node_1[1]
            # print('stop frame:', frame, 'stop y:', current_node_1[1])   
            break
    

    abs_angle_differences = [abs(diff_angle) for frame_value, curr_angle_ba, current_angle_ca, diff_angle in angle_differences]
    # return max_slip_angle, max_distance_gap
    max_slip_angle = max(abs_angle_differences)
    index = abs_angle_differences.index(max_slip_angle)
    max_slip_dist = math.radians(max_slip_angle) * 125
    
    # odb.close()
    return max_slip_dist, max_slip_angle, index

def get_angle_per_frame(odb, step, myInstance, node_1, node_2, contact_node):
    """Calculate the angle between two vectors in 3D space in SUB-ROTATION Step."""
    
    ## Calculate the vectors of nodes for the initial frame
    len_frames = len(step.frames)
    first_frame = step.frames[0]
    first_displacement_field = first_frame.fieldOutputs['U'].getSubset(region=myInstance)
    first_displacement_values = {value.nodeLabel: value for value in first_displacement_field.values}

    node_1_initial_disp = first_displacement_values.get(node_1)
    node_2_initial_disp = first_displacement_values.get(node_2)
    
    try:
        initial_node_1_disp = node_1_initial_disp.data
    except OdbError:
        initial_node_1_disp = node_1_initial_disp.dataDouble
        
    initial_node_1 = [myInstance.nodes[node_1 - 1].coordinates[i] + initial_node_1_disp[i] for i in range(3)]
    
    try: 
        initial_node_2_disp = node_2_initial_disp.data
    except OdbError:
        initial_node_2_disp = node_2_initial_disp.dataDouble
        
    initial_node_2 = [myInstance.nodes[node_2 - 1].coordinates[i] + initial_node_2_disp[i] for i in range(3)]

    initial_vector_ba = [initial_node_1[i] - initial_node_2[i] for i in range(3)]   
    
    ## Calculate the vectors of nodes for each frame
    angles_list = []
    contact_status = True
    for i in range(len_frames):
        frame = i
        new_frame = step.frames[i]
        new_displacement_field = new_frame.fieldOutputs['U'].getSubset(region=myInstance)
        new_displacement_values = {value.nodeLabel: value for value in new_displacement_field.values}
        

        # node 1 (Ground)
        try:
            current_node_1_disp = new_displacement_values[node_1].data
        except OdbError:
            current_node_1_disp = new_displacement_values[node_1].dataDouble
            
        current_node_1 = [myInstance.nodes[node_1 - 1].coordinates[i] + current_node_1_disp[i] for i in range(3)]

        # node 2 (air)
        try:
            current_node_2_disp = new_displacement_values[node_2].data
        except OdbError:
            current_node_2_disp = new_displacement_values[node_2].dataDouble
            
        current_node_2 = [myInstance.nodes[node_2 - 1].coordinates[i] + current_node_2_disp[i] for i in range(3)]
        
        # contact node
        try:
            current_contact_node_disp = new_displacement_values[contact_node].data
        except OdbError:
            current_contact_node_disp = new_displacement_values[contact_node].dataDouble
            
        current_contact_node = [myInstance.nodes[contact_node - 1].coordinates[i] + current_contact_node_disp[i] for i in range(3)]

        current_vector_ba = [current_node_1[i] - current_node_2[i] for i in range(3)]

        
        ## Calculate the frame where the contact stopped, that is why we need "contact_node"
        if current_contact_node[1] > -79:
            contact_status = False
            stop_frame = frame
        else: 
            contact_status = True
            
             
        current_angle_ba = calculate_angle_between_vectors(current_vector_ba, initial_vector_ba)
        abs_current_angle_ba = abs(current_angle_ba)   
        angles_list.append((frame, abs_current_angle_ba))
        
        
        if contact_status == False:
            current_contact_node[1]
            # print('stop frame:', frame, 'stop y:', current_node_1[1])   
            break
        
    # odb.close()
    return angles_list

def calculate_angle_between_vectors(v1, v2):
    """Calculate the angle between two vectors in 3D space."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    # Avoid invalid values for acos
    cos_theta = dot_product / (norm_v1 * norm_v2)
    cos_theta = max(-1.0, min(1.0, cos_theta))  # Clamp values to valid range
    return math.degrees(math.acos(cos_theta))


def contact_area_extraction(odb_name):
    print("...Contact Area Extraction...")
# CSV output file
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    csv_path_name = os.path.join('results','CAREA', csv_file_name)
    with open(csv_path_name, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerow(['Step', 'Time', 'CAREA'])

        # for odb_name in odb_files:
        
        # Open the ODB file
        odb = openOdb(path=odb_name, readOnly=True)
        step_names = list(odb.steps.keys())
        # Iterate over steps
        
        for step_name in step_names[1:]:
            step = odb.steps[step_name]

            node_set_name = None  # Reset the node set name

            # Search for the target history output in history regions
            for region_name in step.historyRegions.keys():
                history_region = step.historyRegions[region_name]
                if 'CAREA    ASSEMBLY_TIRE/ASSEMBLY_GROUND' in history_region.historyOutputs.keys():
                    node_set_name = region_name                    
                    break

            # Extract the CAREA data
            history_region = step.historyRegions[node_set_name]
            carea_data = history_region.historyOutputs['CAREA    ASSEMBLY_TIRE/ASSEMBLY_GROUND'].data
            # Write CAREA data to CSV and print
            
            if carea_data:
                for time, area in carea_data:
                        csvwriter.writerow([step_name,'{:.6f}'.format(time), '{:.6f}'.format(area)])   
            else:
                print("No CAREA data found for step: {}".format(step_name))
                pass
            
                
            

                # print("Step: {}, Time: {}, CAREA: {}".format(step_name, time, area))
    print("Contact Area extraction completed.\n") 
    odb.close()
      
        
def max_stress_extraction(odb_name, instance_name):
    print("...Max Stress Extraction...")
    
    odb = openOdb(odb_name)

    # Change variables
    # 1. Change odb_name
    # 2. Change instance_name
    # 3. Change lastframe_steps
    # 4. Change excluded_steps(= lastframe_steps)

        # Take odb file name and instance name

    # Take only the last frames
    results = []
    max_overall_stress = -float("inf")  #
    max_overall_element = None          #  
    max_overall_step = None             #
    max_overall_frame = None            #
    
    lastframe_steps = ['bending', 'loading', 'loading_300N']

    for step_name in lastframe_steps:
        step = odb.steps[step_name]
        n = len(step.frames)

        # for loop through every frame and an instance             
        stress_field = step.frames[-1].fieldOutputs['S'].getSubset(position = INTEGRATION_POINT, region = odb.rootAssembly.instances[instance_name])
        stress_value = stress_field.values      

        # Find max stress and the element number     
        max_stress_value = -float("inf")
        max_element_label = None

        for stress in stress_value:
            try:
                S11, S22, S33 = stress.data[0], stress.data[1], stress.data[2]
            except OdbError:
                S11, S22, S33 = stress.dataDouble[0], stress.dataDouble[1], stress.dataDouble[2]
                
            traceS = S11 + S22 + S33

            if traceS >= 0:
                if stress.mises > max_stress_value:
                    max_stress_value = stress.mises
                    max_element_label = stress.elementLabel

        results.append([odb_name, step_name, n, instance_name, max_element_label, "{:.6f}".format(max_stress_value)])
        
        if max_stress_value > max_overall_stress:
            max_overall_stress = max_stress_value
            max_overall_element = max_element_label
            max_overall_step = step_name
            max_overall_frame = n  
                  
    # for loop through each step(exclude the previous steps)
    excluded_steps = {"bending", "loading"}
    for step_name in odb.steps.keys():
        if step_name in excluded_steps:
            continue
        step = odb.steps[step_name]
        n = len(step.frames)

        # for loop through every frame          
        for i in range(n):
            stress_field = step.frames[i].fieldOutputs['S'].getSubset(position = INTEGRATION_POINT, region = odb.rootAssembly.instances[instance_name])
            # stress_field = step.frames[i].fieldOutputs['S'].getSubset(position = ELEMENT_NODAL, region = odb.rootAssembly.instances[instance_name])
            stress_value = stress_field.values      

            # Find max stress and the element number           
            max_stress_value = -float("inf")
            max_element_label = None

            for stress in stress_value:
                
                try:
                    S11, S22, S33 = stress.data[0], stress.data[1], stress.data[2]
                except OdbError:
                    S11, S22, S33 = stress.dataDouble[0], stress.dataDouble[1], stress.dataDouble[2]
                    
                traceS = S11 + S22 + S33

                if traceS >= 0:
                    if stress.mises > max_stress_value:
                        max_stress_value = stress.mises
                        max_element_label = stress.elementLabel
        
        results.append([odb_name, step_name, n, instance_name, max_element_label, "{:.6f}".format(max_stress_value)])
        
        if max_stress_value > max_overall_stress:
            max_overall_stress = max_stress_value
            max_overall_element = max_element_label
            max_overall_step = step_name
            max_overall_frame = n  
    print("Max Overall Stress: {}\n".format(max_overall_stress))
    odb.close()    
    return max_overall_stress, max_overall_element, max_overall_step, max_overall_frame
        

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

    force_ori = 200
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
    
    # # CSV 파일 작성 및 저장
    # csv_filename = 'force_displacement_stiffness_results.csv'
    # with open(csv_filename, mode='w') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow(['Time', 'Displacement U2', 'Force (N)', 'Stiffness (N/mm)'])
    #     for time, displacement, force, stiffness in zip(time_graph, displacement_graph, force_graph, stiffness_graph):
    #         csvwriter.writerow([time, displacement, force, stiffness])

    if graph_plot == True:
        
        # FD 그래프 Plot
        plt.figure(figsize=(10, 6))
        plt.plot(displacement_graph, force_graph, marker='o', linestyle='-', color='g', label='Force-Displacement Curve')

        plt.xlabel("Displacement (mm)")
        plt.ylabel("Force (N)")
        plt.title("Force-Displacement Curve")
        plt.grid(True)
        plt.legend()
        plt.savefig('FD_Curve.png')
        plt.show()

        # 강성 그래프 Plot
        plt.figure(figsize=(10, 6))
        plt.plot(time_graph[1:], stiffness_graph[1:], marker='x', linestyle='--', color='r', label='Stiffness over Time')

        plt.xlabel("Time (s)")
        plt.ylabel("Stiffness (N/mm)")
        plt.title("Time-Stiffness Curve")
        plt.grid(True)
        plt.legend()
        plt.savefig('Time-Stiffness Curve.png')
        plt.show()
    return average_stiffness


def bending_moment_extraction(odb_name):
    print("...Bending Moment Extraction...")
    odb = openOdb(path=odb_name, readOnly=True)
    
    step = odb.steps['bending']
    node_set_name = 'L1'
    node_set = odb.rootAssembly.nodeSets[node_set_name]
    assembly_node_label = node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    node_name = 'Node ASSEMBLY.{}'.format(assembly_node_label)
    
    try:
        history_region = step.historyRegions[node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.2' not found in odb file: {}".format(odb_name))
        
    L1_RM3 = history_region.historyOutputs['RM3'].data
    bending_moment = L1_RM3[-1][-1]
    bending_moment = abs(bending_moment)*2
    print("Bending Moment: {}\n".format(bending_moment))
    return bending_moment


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
    with open(csv_path_name, 'wb') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(torque)

    return torque_last_frame, max_torque