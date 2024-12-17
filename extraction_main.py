from extraction_source import *
import os
import pdb
# You should make a list of odb file paths
# odb_files = ['./omniwheel_ref/Design_IDEA3.odb']

odb_folder_path = './omniwheel_ref'
odb_files = [
    os.path.join(odb_folder_path, file)
    for file in os.listdir(odb_folder_path)
    if file.endswith(".odb") and os.path.isfile(os.path.join(odb_folder_path, file))]

instance_name = 'TIRE-1'

odb_name_list = []
max_slip_angle_list = []
max_slip_distance_list = []
vertical_stiffness_list = []
max_overall_stress_list = []
for odb_name in odb_files:
    
    max_slip_angle, max_slip_distance = slip_angle_dist_extraction(odb_name, instance_name)
    vertical_stiffness = stiffness_extraction(odb_name, instance_name)
    max_overall_stress, max_overall_element, max_overall_step, max_overall_frame =max_stress_extraction(odb_name, instance_name)
    contact_area_extraction(odb_name)

    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    odb_name_list.append(odb_base_name)
    max_slip_angle_list.append(max_slip_angle)
    max_slip_distance_list.append(max_slip_distance)
    vertical_stiffness_list.append(vertical_stiffness)
    max_overall_stress_list.append(max_overall_stress)
    
    
    
    # write csv for sungneung yoso
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    csv_file_name = os.path.join('results','Total_results', csv_file_name)
    headers = ["ODB Name", "Max Overall Stress", "Vertical Stiffness", "Max Slip Angle", "Max Slip Distance"]
    values = [odb_base_name, max_overall_stress, vertical_stiffness, max_slip_angle, max_slip_distance]

    with open(csv_file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(headers)
    
        writer.writerow(values)
        

with open("Total_results.csv", "wb") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ODB Name", "Max Slip Angle", "Max Slip Distance", "Vertical Stiffness", "Max Overall Stress"])
    for i in range(len(odb_name_list)):
        writer.writerow([
            odb_name_list[i],
            max_slip_angle_list[i],
            max_slip_distance_list[i],
            vertical_stiffness_list[i],
            max_overall_stress_list[i]
        ])


