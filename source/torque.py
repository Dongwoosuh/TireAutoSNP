# -*- coding: utf-8 -*- 
import os
import csv
import numpy as np

from odbAccess import *

__all__ = ['torque_extraction']

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