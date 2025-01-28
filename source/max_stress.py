# -*- coding: utf-8 -*- 
import os
import csv

from odbAccess import *

__all__ = ['max_stress_extraction']

def max_stress_extraction(odb_name, instance_name, new_target_step_frame_list):
    print("...Max Stress Extraction...")
    
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

    len_loading_frames = len(step_loading.frames)
    
    target_step_frame = [['bending', len_bending_frames-1 ], ['loading_300N', len_loading_frames-1]]
    
    for new_target_step_frame in new_target_step_frame_list:
        target_step_frame.append(new_target_step_frame)
        
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
    
    
    # CSV output file
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    csv_path_name = os.path.join('results','Stress', csv_file_name)
    
    with open(csv_path_name, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerow(['Step', 'Frame', 'ElementLabel', 'Stress'])

        for step_name, frame_num in target_step_frame:
            step = odb.steps[step_name]
            
            stress_field = step.frames[frame_num].fieldOutputs['S'].getSubset(position = INTEGRATION_POINT, region = odb.rootAssembly.instances[instance_name])
            stress_value = stress_field.values
            
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
                        
            csvwriter.writerow([step_name, frame_num, max_element_label, max_stress_value])
                
            if max_stress_value > max_overall_stress:
                max_overall_stress = max_stress_value
                max_overall_element = max_element_label
                max_overall_step = step_name
                max_overall_frame = frame_num
            
    print("Max Overall Stress: {}\n".format(max_overall_stress))
    odb.close()    
    return max_overall_stress, max_overall_element, max_overall_step, max_overall_frame