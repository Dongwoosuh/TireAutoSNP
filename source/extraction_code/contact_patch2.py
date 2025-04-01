# -*- coding: utf-8 -*- 
import os
import csv
import pdb
from odbAccess import *

__all__ = ['contact_area_mean_extraction']

def contact_area_mean_extraction(odb_name):
    print("...Contact Area Extraction...")
# CSV output file
    first_frame_contact_area = None
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
            
            # if step_name == 'subrotation':
            #     first_frame_contact_area  = carea_data[0][1]
            if step_name == 'subrotation':
                carea_list = []
                for time, area in carea_data:
                    if isinstance(area, (int, float)):
                        # print(area)
                        carea_list.append(area)
                # print(carea_list)
                frame_count = len(carea_list)
                # print(frame_count)
                mean_contact_area = 0
                for i in range(frame_count ):
                    mean_contact_area += carea_list[i]

                contact_area_average = float(mean_contact_area) / float(frame_count)
                print(contact_area_average )
                # first_frame_contact_area = sum(carea_list) / frame_count if frame_count > 0 else 0.0

            if carea_data:
                for time, area in carea_data:
                        csvwriter.writerow([step_name,'{:.6f}'.format(time), '{:.6f}'.format(area)])   
            else:
                print("No CAREA data found for step: {}".format(step_name))
                pass
            
                
        

            # print("Step: {}, Time: {}, CAREA: {}".format(step_name, time, area))
    print("Contact Area extraction completed.\n") 
    odb.close()
            
    return contact_area_average
            
            