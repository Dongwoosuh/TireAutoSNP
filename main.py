from source.extraction_code import *
import os
import csv
import pdb

results_folder = './results'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

required_subfolders = ['CAREA', 'Stress_all', 'Tire_center', 'Torque', 'Total_results']

for subfolder in required_subfolders:
    subfolder_path = os.path.join(results_folder, subfolder)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
        print("{} folder has been created".format(subfolder_path))
    else:
        print("{} is already exist".format(subfolder_path))

        

odb_folder_path = './omniwheel_ref'
odb_files = [
    os.path.join(odb_folder_path, file)
    for file in os.listdir(odb_folder_path)
    if file.endswith(".odb") and os.path.isfile(os.path.join(odb_folder_path, file))]

# odb_files = [os.path.join(odb_folder_path, 'Run15.odb')]

instance_name = 'TIRE-1'

odb_name_list = []
max_overall_stress_list = []
# avg_vertical_stiffness_list = []
# last_vertical_stiffness_list = []
# initial_vertical_stiffness_list = []
displacement_last_frame_list = []
max_slip_angle_list = []
max_slip_distance_list = []
bending_moment_list = []
torque_list = []
subrot_center_disp_gap_list = []
rot_center_disp_gap_list = []
total_cetner_disp_gap_list = []
total_center_disp_std_list = []
max_velocity_subrot_list = []
max_velocity_rot_list = []
target_contact_area_list = []
subrot_stoptime_list = []
rot_stoptime_list = []
max_rot_carea_list = []

for odb_name in odb_files:
    print("\n====================== Extracting data from {} ===========================".format(odb_name))
    
    max_slip_angle, subrot_stoptime, max_angle_index= slip_angle_extraction(odb_name, instance_name) # using last frame and first frame
    max_slip_distance, rot_stoptime , max_dist_idx= slip_distance_extraction(odb_name, instance_name) # using last frame and first frame
    # max_slip_angle, max_slip_distance, target_step_frame_list, subrot_stoptime, rot_stoptime, outlier_bool  = slip_angle_dist_extraction(odb_name, instance_name)
    
    # # do not save the data if outlier_bool is True
    # if outlier_bool:
    #     continue
    
    target_step_frame_list = [['subrotation', max_angle_index-1], ['rotation', max_dist_idx-1]]
    
    displacement_last_frame = vertical_stiffness_extraction(odb_name, instance_name) # using last frame and first frame
    target_contact_area_, max_rot_carea  = contact_area_extraction(odb_name)
    subrot_center_disp_gap, rot_center_disp_gap, total_ceter_disp_gap, total_center_disp_std, max_velocity_subrot, max_velocity_rot = tire_center_displacement_extraction(odb_name)
    bending_moment = bending_moment_extraction(odb_name)
    torque_last_frame, max_torque = torque_extraction(odb_name)
    contact_area_extraction(odb_name)
    target_contact_area = contact_area_mean_extraction(odb_name)
    
    max_stress_extraction(odb_name, instance_name, target_step_frame_list)

    ## CSV output file
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    odb_name_list.append(odb_base_name)
    
    
    target_contact_area_list.append(target_contact_area)    
    # displacement_last_frame_list.append(displacement_last_frame)
    max_slip_angle_list.append(max_slip_angle)
    max_slip_distance_list.append(max_slip_distance)
    bending_moment_list.append(bending_moment)
    torque_list.append(torque_last_frame)
    subrot_center_disp_gap_list.append(subrot_center_disp_gap)
    rot_center_disp_gap_list.append(rot_center_disp_gap)
    total_cetner_disp_gap_list.append(total_ceter_disp_gap)
    total_center_disp_std_list.append(total_center_disp_std)
    max_velocity_subrot_list.append(max_velocity_subrot)
    max_velocity_rot_list.append(max_velocity_rot)
    subrot_stoptime_list.append(subrot_stoptime)
    rot_stoptime_list.append(rot_stoptime)
    max_rot_carea_list.append(max_rot_carea)
    
    
    # write csv for sungneung yoso
    odb_base_name = os.path.basename(odb_name).replace(".odb", "")
    csv_file_name = os.path.basename(odb_name).replace(".odb", ".csv")
    csv_file_name = os.path.join('results','Total_results', csv_file_name)
    headers = ["ODB Name", 
            #    "Vertical Stiffness",
               "Max Slip Angle",
               "Max Slip Distance",
               "Bending Moment",
               "Torque", 
               "Center Disp Gap(subrot)", 
               "Center Disp Gap(rot)",
               "Total Center Disp Gap",
               "Total Center Disp Std",
               "Max Velocity(subrot)",
               "Max Velocity(rot)", 
               "Target Contact Area",
               "Subrot Stop Time",
               "Rot Stop Time",
               "Max Rot Contact Area"] 
    values = [odb_base_name, 
            #   displacement_last_frame,
              max_slip_angle, 
              max_slip_distance, 
              bending_moment, 
              torque_last_frame, 
              subrot_center_disp_gap,
              rot_center_disp_gap, 
              total_ceter_disp_gap,
              total_center_disp_std,
              max_velocity_subrot,
              max_velocity_rot, 
              target_contact_area,
              subrot_stoptime, 
              rot_stoptime, 
              max_rot_carea]

    with open(csv_file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerow(values)

    print("======================== Data extraction and file creation completed. ===========================\n")

    

    Total_results_file = os.path.join('results', 'Total_results_all.csv')
    with open(Total_results_file, "wb") as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow (["ODB Name", "Vertical Stiffness"] )
        # writer.writerow (["ODB Name", "Vertical Stiffness", "Subrot Stop Time", "Rot Stop Time"] )
        # writer.writerow(["ODB Name", "Vertical Stiffness", "Max Slip Angle", "Max Slip Distance", "Bending Moment", "Torque", "Center Disp Gap(subrot)", "Center Disp Gap(rot)", "Total Center Disp Gap", "Total Center Disp Std", "Max Velocity(subrot)", "Max Velocity(rot)", "Target Contact Area", "Subrot Stop Time", "Rot Stop Time"])
        writer.writerow(["ODB Name",
                        "Vertical Stiffness",
                        "Max Slip Angle", 
                        "Max Slip Distance",
                        "Bending Moment", 
                        "Torque", 
                        "Center Disp Gap(subrot)",
                        "Center Disp Gap(rot)",
                        "Total Center Disp Gap", 
                        "Total Center Disp Std", 
                        "Max Velocity(subrot)",
                        "Max Velocity(rot)",
                        "Target Contact Area", 
                        "Subrot Stop Time", 
                        "Rot Stop Time", 
                        "Max Rot Contact Area"])

        for i in range(len(odb_name_list)):
            writer.writerow([
                odb_name_list[i],

                displacement_last_frame_list[i],
                max_slip_angle_list[i],
                max_slip_distance_list[i],
                bending_moment_list[i],
                torque_list[i],
                subrot_center_disp_gap_list[i],
                rot_center_disp_gap_list[i],
                total_cetner_disp_gap_list[i],
                total_center_disp_std_list[i],
                max_velocity_subrot_list[i],
                max_velocity_rot_list[i],
                target_contact_area_list[i],
                subrot_stoptime_list[i],
                rot_stoptime_list[i],
                max_rot_carea_list[i]
                ])
        

