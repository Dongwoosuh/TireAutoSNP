# -*- coding: utf-8 -*- 
import os
import csv
import sys
import pdb
from odbAccess import *

__all__ = ['max_stress_and_LE_extraction']

def max_stress_and_LE_extraction(odb_name, instance_name, new_target_step_frame_list):
    print("...Max Stress and LE Extraction...")
    
    odb = openOdb(odb_name)
    
    try:
        step_bending = odb.steps['bending']
    except KeyError:
        print("Error: No bending")
        odb.close()
        exit()

    len_bending_frames = len(step_bending.frames)
    try:
        step_loading = odb.steps['loading_300N']
    except KeyError:
        print("Error: No bending")
        odb.close()
        exit()
        
    try:
        step_subrotation = odb.steps['subrotation']
        subrotation_time = [frame.frameValue for frame in step_subrotation.frames]
    except KeyError:
        print("Error: No subrotation")
        odb.close()
        exit()
        
    try:
        step_rotation = odb.steps['rotation']
        rotation_time = [frame.frameValue for frame in step_rotation.frames]
    except KeyError:
        print("Error: No rotation")
        odb.close()
        exit()
        
    for i in new_target_step_frame_list:
        if i[0] == 'subrotation':
            for j in range(len(subrotation_time)):
                if subrotation_time[j] >= i[1]:
                    subrotation_frame = j-1
                    break
                
        elif i[0] == 'rotation':
            for j in range(len(rotation_time)):
                if rotation_time[j] >= i[1]:
                    rotation_frame = j-1
                    break
                
    len_loading_frames = len(step_loading.frames)
    
    target_step_frame = [['bending', len_bending_frames-1 ], ['loading_300N', len_loading_frames-1], ['subrotation', subrotation_frame], ['rotation', rotation_frame]]

    # CSV output files setup
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    
    stress_csv_path = os.path.join('results','Stress_all', csv_file_name)
    le_csv_path = os.path.join('results', 'LE_all', csv_file_name)
    
    stress_steps_data = {}
    le_steps_data = {}
    all_elements_label = set()

    for step_name, frame_num in target_step_frame:
        step = odb.steps[step_name]
        
        # Define region
        region = odb.rootAssembly.instances[instance_name]
        
        # Extract Stress
        stress_field = step.frames[frame_num].fieldOutputs['S'].getSubset(position = INTEGRATION_POINT, region = region)
        stress_value = stress_field.values
        
        # Extract LE
        le_field = step.frames[frame_num].fieldOutputs['LE'].getSubset(position = INTEGRATION_POINT, region = region)
        le_value = le_field.values
        
        step_key = (step_name, frame_num)
        stress_steps_data[step_key] = {}
        le_steps_data[step_key] = {}
        
        # Process Stress
        for stress in stress_value:
            stress_steps_data[step_key][stress.elementLabel] = stress.mises
            all_elements_label.add(stress.elementLabel)
            
        # Process LE
        for le in le_value:
            le_steps_data[step_key][le.elementLabel] = le.maxPrincipal
            all_elements_label.add(le.elementLabel)
                            
    all_element_labels  = sorted(all_elements_label)
    
    if sys.version_info[0] < 3:
        mode = 'wb'
        kwargs = {}
    else:
        mode = 'w'
        kwargs = {'newline': ''}

    # Write Stress CSV
    with open(stress_csv_path, mode, **kwargs) as f:
        writer = csv.writer(f, lineterminator='\n')
        header = ['ElementLabel']
        for step_name, frame_num in target_step_frame:
            header.append("{}_{}".format(step_name, frame_num))
        writer.writerow(header)

        for elem_label in all_element_labels:
            row = [elem_label]
            for step_name, frame_num in target_step_frame:
                step_key = (step_name, frame_num)
                val = stress_steps_data[step_key].get(elem_label, None)
                row.append(val)
            writer.writerow(row)
            
    # Write LE CSV
    with open(le_csv_path, mode, **kwargs) as f:
        writer = csv.writer(f, lineterminator='\n')
        header = ['ElementLabel']
        for step_name, frame_num in target_step_frame:
            header.append("{}_{}".format(step_name, frame_num))
        writer.writerow(header)

        for elem_label in all_element_labels:
            row = [elem_label]
            for step_name, frame_num in target_step_frame:
                step_key = (step_name, frame_num)
                val = le_steps_data[step_key].get(elem_label, None)
                row.append(val)
            writer.writerow(row)
                
    print("...Max Stress and LE Extraction Completed...")
    odb.close()
