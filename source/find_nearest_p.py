import numpy as np
from odbAccess import openOdb, OdbError
import math
import pdb

# def find_node_with_min_y(nodes, displacement_values):
#     min_y = float('inf')
#     min_y_node = None
#     for node in nodes:
#         disp = displacement_values.get(node.label)
#         if disp is None:
#             continue

#         try:
#             y = node.coordinates[1] + disp.data[1]  #
#         except OdbError:  
#             y = node.coordinates[1] + disp.dataDouble[1]
        
        
#         if y < min_y:
#             min_y = y
#             min_y_node = node

#     return min_y_node

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



def find_closest_node_to_target(nodes, target_node, displacement_values):
    closest_node = None
    min_distance = float('inf')

    
    target_disp = displacement_values.get(target_node.label)
    if target_disp is not None:
        try:
            target_coordinates = [
                target_node.coordinates[0] + target_disp.data[0],
                target_node.coordinates[1] + target_disp.data[1],
                target_node.coordinates[2] + target_disp.data[2],
            ]
        except OdbError:
            target_coordinates = [
                target_node.coordinates[0] + target_disp.dataDouble[0],
                target_node.coordinates[1] + target_disp.dataDouble[1],
                target_node.coordinates[2] + target_disp.dataDouble[2],
            ]
    else:

        target_coordinates = target_node.coordinates

    
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
        
        if node_coordinates[0] > 90 and node_coordinates[1] < -79.9 : 
            
            distance = np.linalg.norm(np.array(node_coordinates) - np.array(target_coordinates))

            if distance < min_distance:
                min_distance = distance
                closest_node = node

    return closest_node
