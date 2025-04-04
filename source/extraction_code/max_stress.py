# -*- coding: utf-8 -*- 
import os
import csv
import pdb
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
    # for new_target_step_frame in new_target_step_frame_list:
    #     target_step_frame.append(new_target_step_frame)
        
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
    csv_path_name = os.path.join('results','Stress_all', csv_file_name)
    
    steps_data = {}
    all_elements_label = set()

    for step_name, frame_num in target_step_frame:
        step = odb.steps[step_name]

        stress_field = step.frames[frame_num].fieldOutputs['S'].getSubset(position = INTEGRATION_POINT, region = odb.rootAssembly.instances[instance_name])
        stress_value = stress_field.values
        
        max_stress_value = -float("inf")
        max_element_label = None
        
        step_key = (step_name, frame_num)
        steps_data[step_key] = {}
        
        for stress in stress_value:
            try:
                S11, S22, S33 = stress.data[0], stress.data[1], stress.data[2]
            except OdbError:
                S11, S22, S33 = stress.dataDouble[0], stress.dataDouble[1], stress.dataDouble[2]
                
            traceS = S11 + S22 + S33

            steps_data[step_key][stress.elementLabel] = stress.mises
            all_elements_label.add(stress.elementLabel)
    
                # if traceS >= 0:
                #     if stress.mises > max_stress_value:
                #         max_stress_value = stress.mises
                #         max_element_label = stress.elementLabel
                            
    all_element_labels  = sorted(all_elements_label)
    
    with open(csv_path_name, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')

        # 헤더: Step, Frame, 그리고 모든 Element Label
        header = ['ElementLabel']
        for step_name, frame_num in target_step_frame:
            header.append("{}_{}".format(step_name, frame_num))
        writer.writerow(header)


        # 2) 요소별로 한 행씩
        for elem_label in all_element_labels:
            row = [elem_label]
            # case_keys 순서대로 traceS를 가져옴
            for step_name, frame_num in target_step_frame:
                step_key = (step_name, frame_num)
                # 해당 케이스에 이 요소가 있다면 traceS, 없으면 None
                trace_s = steps_data[step_key].get(elem_label, None)
                row.append(trace_s)
            
            writer.writerow(row)
                
    print("...Max Stress Extraction Completed...")
    odb.close()    