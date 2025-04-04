# -*- coding: utf-8 -*- 
import sys
import math
import numpy as np
import pdb

from odbAccess import *
from find_nearest_p import *

__all__ = ['slip_angle_dist_extraction']    

def load_step(odb, step_name):
    try:
        step = odb.steps[step_name]
    except KeyError:
        print("Error: No step named", step_name)
        odb.close()
        sys.exit()
    return step

def slip_angle_dist_extraction(odb_name, instance_name):
    print("...Slip Angle and Distance Extraction...")
    
    try:
        odb = openOdb(path=odb_name, readOnly=True)
    except OdbError as e:
        print("No ODB")
        exit()

    step_bending = load_step(odb, 'bending')
    step_subrotation = load_step(odb, 'subrotation')
    step_rotation = load_step(odb, 'rotation')
    
    len_frames = len(step_bending.frames)

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
    target_point_1 = (node_a_initial_x + 5, node_a_initial_y , node_a_initial_z)
    target_point_2 = (node_a_initial_x + 5, node_a_initial_y + 30 , node_a_initial_z)
    
    # the node closest to the target point in the initial frame (Node B)
    closest_node_1 = find_closest_node(target_point_1, myInstance.nodes, displacement_values_initial)
    if closest_node_1:
        node_a = closest_node_1.label
        # node_a = closest_node_1
    else:
        print("Error: Could not find a node closest to the target point in initial frame.")
        
    closest_node_2 = find_closest_node(target_point_2, myInstance.nodes, displacement_values_initial)
    if closest_node_2:
        node_b = closest_node_2.label
        # node_b = closest_node_2
    else:
        print("Error: Could not find a node closest to the target point in initial frame.")
        
    # pdb.set_trace()
    # close_nodes_b, close_nodes_b_coords = find_nodes_within_tolerance(target_point, myInstance.nodes, displacement_values_initial)
    # node_b_coords = calculate_midpoint_by_nodes(close_nodes_b_coords)
    

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
    
    
    target_point_e = (node_c_x, 0 , node_c_z)
    # print(target_point_e)
    closest_node_e = find_closest_node(target_point_e, myInstance.nodes, displacement_values_initial)
    if closest_node_e:
        node_e = closest_node_e.label
        
    else:
        print("Error: Could not find a node closest to the target point in initial frame.")
    
    # target_point_e = (0, 0 , 0)
    # # print(target_point_e)
    # close_nodes_e, close_nodes_e_coords = find_nodes_within_tolerance(target_point_e, myInstance.nodes, displacement_values_initial)
    # node_e_coords = calculate_midpoint_by_nodes(close_nodes_e_coords) 
    

    last_frame_subrotation = step_subrotation.frames[-1]

    # Get the displacement field output for the specific instance
    displacement_field_last_subrotation = last_frame_subrotation.fieldOutputs['U'].getSubset(region=myInstance)

    # Create a dictionary mapping node labels to displacement values for the instance
    displacement_values_last_subrotation = {value.nodeLabel: value for value in displacement_field_last_subrotation.values}
    # Now, proceed with finding the node with minimum Y coordinate
    # min_y_node_D = find_node_with_min_y(myInstance.nodes, displacement_values_last_subrotation)
    min_y_node_D = find_closest_node_to_target(myInstance.nodes , displacement_values_last_subrotation)

    if min_y_node_D:
        node_d = min_y_node_D.label


    ## Print the nodes for verification
    print("Last frame: Node with min Y (Node A): {}".format(node_a))
    print("Initial frame: Node closest to target point (Node B): {}".format(node_b))
    print("Initial frame: Node with min Y among nodes with min X (Node C): {}".format(node_c))
    print("Last frame of 'rotation' step: Node with min Y (Node D): {}".format(node_d))
    print("node e: {}\n".format(node_e))


    # Get the angle difference between noce A, B
    angleslist_ba, subrot_stoptime, outlier_bool, time_list = get_angle_per_frame(odb, step_subrotation, myInstance, node_a, node_b, contact_node=node_a)
    # Get the angle difference between noce C, E
    ###### not used
    angleslist_ec, _, _, _ = get_angle_per_frame(odb, step_subrotation, myInstance, node_c, node_e, contact_node=node_a)
    angle_differences = [abs(a[1] - b[1]) for a, b in zip(angleslist_ba, angleslist_ec)]
    print(angle_differences)
    pdb.set_trace()
    
    ######
    velocity_of_subrot = 4.63*2
    angleslist_ec = [math.degrees(velocity_of_subrot*time) for time in time_list]
    
    angle_differences = [abs(a[1] - b) for a, b in zip(angleslist_ba, angleslist_ec)]
    
    print(angle_differences)
    max_angle_difference = max(angle_differences)
    max_angle_index = angle_differences.index(max_angle_difference)
    
    #### The way to find the max angle difference with the first PEAK frame
    # max_angle_difference = angle_differences[0]
    
    # for i in range(1, len(angle_differences)): 
    #     if angle_differences[i] > max_angle_difference:
    #         max_angle_difference = angle_differences[i]
    #     else:
    #         break            
    # max_angle_index = angle_differences.index(max_angle_difference)
    
    print("Max angle difference: {} at frame {}".format(max_angle_difference, max_angle_index))
    
    
    # Get the slip distance between node D and node B
    if len(step_rotation.frames) == 0:
        max_slip_distance = 'No Rotation Step'
        idx = 'No Rotation Step'
        target_step_frame = [['subrotation', max_angle_index-1]]
        rot_stoptime = 'No Rotation Step'
    else:
        # max_slip_distance_ori, _, max_dist_idx, rot_stoptime,  = get_slip_dist(odb, step_rotation, myInstance, node_d, node_b)
        max_slip_distance, _, max_dist_idx, rot_stoptime = get_slip_dist_with_tire_center(odb, step_rotation, myInstance, node_d)

        print("Max distance gap: {} at frame {}\n".format(max_slip_distance, max_dist_idx))
        
        target_step_frame = [['subrotation', max_angle_index-1], ['rotation', max_dist_idx-1]]
    
    return max_angle_difference, max_slip_distance, target_step_frame, subrot_stoptime, rot_stoptime, outlier_bool

def get_slip_dist(odb, step, myInstance, node_1, node_2):
    """Calculate the slip distance between two nodes in 3D space in ROTATION Step."""
    stop_time = "Value error"
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
    
    # initial_node_2 = calculate_center_of_nodes(myInstance, node_2, first_displacement_field)
    try: 
        initial_node_2_disp = node_2_initial_disp.data
    except OdbError:
        initial_node_2_disp = node_2_initial_disp.dataDouble
        
    initial_node_2 = [myInstance.nodes[node_2 - 1].coordinates[i] + initial_node_2_disp[i] for i in range(3)]
    initial_vector_ba = [initial_node_1[i] - center2_initial_coords[i] for i in range(3)]
    initial_vector_ca = [initial_node_2[i] - center2_initial_coords[i] for i in range(3)]
    
    ## Calculate the vectors of nodes for each frame
    angle_differences = []
    time_list = []
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
        # current_node_2 = calculate_center_of_nodes(myInstance, node_2, new_displacement_field)
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
        
        if current_node_1[1] > -79.99:
            contact_status = False
        else: 
            contact_status = True
            
             
        current_angle_ba = calculate_angle_between_vectors(current_vector_ba, initial_vector_ba)
        current_angle_ca = calculate_angle_between_vectors(current_vector_ca, initial_vector_ca)
        angle_difference_1 = current_angle_ba - current_angle_ca
        angle_differences.append((frame, current_angle_ba, current_angle_ca, angle_difference_1))
                
        if contact_status == False:
            current_node_1[1]
            stop_time = new_frame.frameValue
            # print('stop frame:', frame, 'stop y:', current_node_1[1])   
            break
    

    abs_angle_differences = [abs(diff_angle) for frame_value, curr_angle_ba, current_angle_ca, diff_angle in angle_differences]
    # return max_slip_angle, max_distance_gap
    max_slip_angle = max(abs_angle_differences)
    max_slip_dist = math.radians(max_slip_angle) * 150
    
    # index1 = abs_angle_differences.index(max_slip_angle)
    index = len(angle_differences)
    # odb.close()
    return max_slip_dist, max_slip_angle, index, stop_time

def get_angle_per_frame(odb, step, myInstance, node_1, node_2, contact_node):
    """Calculate the angle between two vectors in 3D space in SUB-ROTATION Step."""
    outlier_check =0
    outlier_exist = False
    stop_time_ = None
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
    pdb.set_trace()
    # initial_node_2  = calculate_center_of_nodes(myInstance, node_2, first_displacement_field)
    try: 
        initial_node_2_disp = node_2_initial_disp.data
    except OdbError:
        initial_node_2_disp = node_2_initial_disp.dataDouble

    # initial_vector_ba = [initial_node_1[i] - initial_node_2[i] for i in range(3)]   
    initial_node_2 = [myInstance.nodes[node_2 - 1].coordinates[i] + initial_node_2_disp[i] for i in range(3)]

    initial_vector_ba = [initial_node_1[i] - initial_node_2[i] for i in range(3)] 
    
    ## Calculate the vectors of nodes for each frame
    angles_list = []
    time_list = []
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
        
        # current_node_2  = calculate_center_of_nodes(myInstance, node_2, new_displacement_field)   

        # contact node
        try:
            current_contact_node_disp = new_displacement_values[contact_node].data
        except OdbError:
            current_contact_node_disp = new_displacement_values[contact_node].dataDouble
            
        current_contact_node = [myInstance.nodes[contact_node - 1].coordinates[i] + current_contact_node_disp[i] for i in range(3)]

        current_vector_ba = [current_node_1[i] - current_node_2[i] for i in range(3)]
        
        ## Calculate the frame where the contact stopped, that is why we need "contact_node"
        if current_contact_node[1] > -79.99:
            if outlier_check == 0:
                contact_status = False
                outlier_exist =True
                # stop_time_ = new_frame.frameValue
            else:
                contact_status = False
        else: 
            contact_status = True
            outlier_check += 1
            stop_time_ = new_frame.frameValue
            
    
        current_angle_ba = calculate_angle_between_vectors(current_vector_ba, initial_vector_ba)
        abs_current_angle_ba = abs(current_angle_ba)   
        angles_list.append((frame, abs_current_angle_ba))
        time_list.append(new_frame.frameValue)
        
        if contact_status == False:
            current_contact_node[1]
            # print('stop frame:', frame, 'stop y:', current_node_1[1])   
            stop_time_ = new_frame.frameValue
            
        if new_frame.frameValue > 0.05:
            break
    # odb.close()
    return angles_list, stop_time_, outlier_exist, time_list

def calculate_angle_between_vectors(v1, v2):
    """Calculate the angle between two vectors in 3D space."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    # Avoid invalid values for acos
    cos_theta = dot_product / (norm_v1 * norm_v2)
    cos_theta = max(-1.0, min(1.0, cos_theta))  # Clamp values to valid range
    return math.degrees(math.acos(cos_theta))


def get_slip_dist_with_tire_center(odb, step, myInstance, node_1):
    """Calculate the slip distance between two nodes in 3D space in ROTATION Step."""
    stop_time = "Value error"
    center2= odb.rootAssembly.nodeSets['TIRE_CENTER_2']

    len_frames = len(step.frames)
    first_frame = step.frames[0]
    first_displacement_field = first_frame.fieldOutputs['U'].getSubset(region=myInstance)
    first_displacement_values = {value.nodeLabel: value for value in first_displacement_field.values}

    node_1_initial_disp = first_displacement_values.get(node_1)
    
    if node_1_initial_disp is None :
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

    initial_vector_ba = [initial_node_1[i] - center2_initial_coords[i] for i in range(3)]
    
    ## Calculate the vectors of nodes for each frame
    angle_differences = []
    time_list = []
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
        
        
        
        if current_node_1[1] > -79.98:
            contact_status = False
        else: 
            contact_status = True
            
             
        current_angle_ba = calculate_angle_between_vectors(current_vector_ba, initial_vector_ba)
        rotation_velocity = 5.56*2
        true_current_angle = math.degrees(rotation_velocity*new_frame.frameValue)
        angle_difference = current_angle_ba - true_current_angle
        angle_differences.append((frame, current_angle_ba, true_current_angle, angle_difference))
                
        if contact_status == False:
            current_node_1[1]
            stop_time = new_frame.frameValue

        if new_frame.frameValue > 0.035:
            break
    
    ori_angle_differences = [diff_angle for frame_value, curr_angle_ba, true_current_angle, diff_angle in angle_differences]   
    abs_angle_differences = [abs(diff_angle) for frame_value, curr_angle_ba, current_angle_ca, diff_angle in angle_differences]
    
    print(abs_angle_differences)
    # return max_slip_angle, max_distance_gap
    max_slip_angle = max(abs_angle_differences)
    max_slip_dist = math.radians(max_slip_angle) * 150
    
    index = abs_angle_differences.index(max_slip_angle)
    # index = len(angle_differences)

    # odb.close()
    return max_slip_dist, max_slip_angle, index, stop_time
