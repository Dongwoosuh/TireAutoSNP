from source.extraction_source import *
import os
import pdb


odb_folder_path = './omniwheel_ref'
odb_files = [
    os.path.join(odb_folder_path, file)
    for file in os.listdir(odb_folder_path)
    if file.endswith(".odb") and os.path.isfile(os.path.join(odb_folder_path, file))]

instance_name = 'TIRE-1'

odb_name_list = []
max_overall_stress_list = []
vertical_stiffness_list = []
max_slip_angle_list = []
max_slip_distance_list = []
bending_moment_list = []
torque_list = []

for odb_name in odb_files:
    print("\n====================== Extracting data from {} ===========================".format(odb_name))
    
    vertical_stiffness = vertical_stiffness_extraction(odb_name, instance_name)
    max_slip_angle, max_slip_distance = slip_angle_dist_extraction(odb_name, instance_name)
    bending_moment = bending_moment_extraction(odb_name)
    torque_last_frame, max_torque = torque_extraction(odb_name)
    contact_area_extraction(odb_name)
    
    max_overall_stress, max_overall_element, max_overall_step, max_overall_frame =max_stress_extraction(odb_name, instance_name)


    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    odb_name_list.append(odb_base_name)
    max_overall_stress_list.append(max_overall_stress)
    vertical_stiffness_list.append(vertical_stiffness)
    max_slip_angle_list.append(max_slip_angle)
    max_slip_distance_list.append(max_slip_distance)
    bending_moment_list.append(bending_moment)
    torque_list.append(max_torque)
    
    
    # write csv for sungneung yoso
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    csv_file_name = os.path.join('results','Total_results', csv_file_name)
    headers = ["ODB Name", "Max Overall Stress", "Vertical Stiffness", "Max Slip Angle", "Max Slip Distance", "Bending Moment", "Torque"]
    values = [odb_base_name, max_overall_stress, vertical_stiffness, max_slip_angle, max_slip_distance, bending_moment, torque_last_frame]

    with open(csv_file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerow(values)

    print("======================== Data extraction and file creation completed. ===========================\n")

    

Total_results_file = os.path.join('results', 'Total_results.csv')
with open(Total_results_file, "wb") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ODB Name", "Max Overall Stress", "Vertical Stiffness", "Max Slip Angle", "Max Slip Distance", "Bending Moment", "Torque"])
    for i in range(len(odb_name_list)):
        writer.writerow([
            odb_name_list[i],
            max_overall_stress_list[i],
            vertical_stiffness_list[i],
            max_slip_angle_list[i],
            max_slip_distance_list[i],
            bending_moment_list[i],
            torque_list[i]
        ])

