import numpy as np
from odbAccess import openOdb, OdbError
import math
import pdb


def find_node_with_min_y(nodes, displacement_values):
    min_x = float('inf')
    min_y = float('inf')
    min_x_node = None
    min_y_node = None
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue

        try:
            x = node.coordinates[0] + disp.data[0]  #
            y = node.coordinates[1] + disp.data[1]  #
        except OdbError:  
            x = node.coordinates[0] + disp.dataDouble[0]
            y = node.coordinates[1] + disp.dataDouble[1]
        
        if x > 90 : 
            if y < min_y:
                min_y = y
                min_y_node = node
                
        else: 
            continue

    return min_y_node


def find_closest_node(target_point, nodes, displacement_values):

    min_distance = float('inf')
    closest_node = None
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue
        try:
            x = node.coordinates[0] + disp.data[0]
            y = node.coordinates[1] + disp.data[1]
            z = node.coordinates[2] + disp.data[2]
        except OdbError:
            x = node.coordinates[0] + disp.dataDouble[0]
            y = node.coordinates[1] + disp.dataDouble[1]
            z = node.coordinates[2] + disp.dataDouble[2] 
            
        distance = math.sqrt((x - target_point[0])**2 + (y - target_point[1])**2 + (z - target_point[2])**2)
        if distance < min_distance:
            min_distance = distance
            closest_node = node
    return closest_node

def find_nodes_within_tolerance(target_point, nodes, displacement_values, tolerance=3.05):

    close_nodes = []
    close_nodes_coords = []
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue
        try:
            x = node.coordinates[0] + disp.data[0]
            y = node.coordinates[1] + disp.data[1]
            z = node.coordinates[2] + disp.data[2]
        except OdbError:
            x = node.coordinates[0] + disp.dataDouble[0]
            y = node.coordinates[1] + disp.dataDouble[1]
            z = node.coordinates[2] + disp.dataDouble[2]

        distance = math.sqrt((x - target_point[0])**2 + 
                             (y - target_point[1])**2 + 
                             (z - target_point[2])**2)
        if distance < tolerance:
            # if x/target_point[0] > 0.99 and x/target_point[0] < 1.01:
            close_nodes.append(node.label)
            close_nodes_coords.append((x, y, z))    
                
    return close_nodes , close_nodes_coords

def calculate_midpoint_by_nodes(node_coords):
    """
    Calculate the centroid of nodes based on their label-wise positions.

    Args:
        nodes_data (list): List of (node_label, x, y, z) coordinates.

    Returns:
        dict: Dictionary with node labels as keys and their centroid positions as values.
    """

    valid_node_count = 0
    x_sum, y_sum, z_sum = 0.0, 0.0, 0.0
    centroids = {}
    for x, y, z in node_coords:
        x_sum += x
        y_sum += y
        z_sum += z
        valid_node_count += 1
        
    if valid_node_count == 0:
        raise ValueError("No valid nodes found for displacement calculation.")
    
    center_x = x_sum / valid_node_count
    center_y = y_sum / valid_node_count
    center_z = z_sum / valid_node_count

    return (center_x, center_y, center_z)

def calculate_center_of_nodes(myInstance, node_labels, displacement_field):
    """
    Calculate the center point of given nodes based on their displacement values.

    Args:
        node_labels (list): List of node labels.
        displacement_field (FieldOutput): Abaqus displacement field output.

    Returns:
        tuple: (x, y, z) coordinates of the center point.
    """
    displacement_values = {value.nodeLabel: value for value in displacement_field.values}

    x_sum, y_sum, z_sum = 0.0, 0.0, 0.0
    valid_node_count = 0

    for node_label in node_labels:
        node_disp = displacement_values.get(node_label)

        if node_disp is None:
            continue  # Skip if no displacement data found

        try:
            disp = node_disp.data  # Try accessing displacement normally
        except OdbError:
            disp = node_disp.dataDouble  # Fallback for double precision data

        # Calculate displaced coordinates
        x = myInstance.nodes[node_label-1].coordinates[0] + disp[0]
        y = myInstance.nodes[node_label-1].coordinates[1] + disp[1]
        z = myInstance.nodes[node_label-1].coordinates[2] + disp[2]
        # pdb.set_trace()
        x_sum += x
        y_sum += y
        z_sum += z
        valid_node_count += 1

    if valid_node_count == 0:
        raise ValueError("No valid nodes found for displacement calculation.")

    # Calculate the centroid by averaging the positions
    center_x = x_sum / valid_node_count
    center_y = y_sum / valid_node_count
    center_z = z_sum / valid_node_count

    return [center_x, center_y, center_z]

def find_nodes_with_min_x(nodes, displacement_values):

    min_x = float('inf')
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue
        
        try:
            x = node.coordinates[0] + disp.data[0]
        except OdbError:
            x = node.coordinates[0] + disp.dataDouble[0]
            
        if x < min_x:
            min_x = x

    min_x_nodes = []
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue
        
        try:
            x = node.coordinates[0] + disp.data[0]
        except OdbError:
            x = node.coordinates[0] + disp.dataDouble[0]
            
        if abs(x - min_x) < 1e-6:  
            min_x_nodes.append(node)
    return min_x_nodes

def find_node_with_min_y_among(nodes, displacement_values):

    min_y = float('inf')
    min_y_node = None
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue
        
        try:
            y = node.coordinates[1] + disp.data[1]
            
        except OdbError:
            y = node.coordinates[1] + disp.dataDouble[1]
            
        if y < min_y:
            min_y = y
            min_y_node = node
            
    return min_y_node



def find_closest_node_to_target(nodes, displacement_values):
    valid_nodes = []
    
    for node in nodes:
        disp = displacement_values.get(node.label)
        if disp is None:
            continue
        
        try:
            node_coordinates = [
                node.coordinates[0] + disp.data[0],
                node.coordinates[1] + disp.data[1],
                node.coordinates[2] + disp.data[2],
            ]
        except OdbError:
            node_coordinates = [
                node.coordinates[0] + disp.dataDouble[0],
                node.coordinates[1] + disp.dataDouble[1],
                node.coordinates[2] + disp.dataDouble[2],
            ]
        
        if node_coordinates[0] > 90 and node_coordinates[1] < -79.9:
            valid_nodes.append((node, node_coordinates))

    if not valid_nodes:
        return None


    mean_coordinates = np.mean([coords for _, coords in valid_nodes], axis=0)


    closest_node = None
    min_distance = float('inf')

    for node, node_coordinates in valid_nodes:
        distance = np.linalg.norm(np.array(node_coordinates) - np.array(mean_coordinates))
        if distance < min_distance:
            min_distance = distance
            closest_node = node  

    return closest_node  
