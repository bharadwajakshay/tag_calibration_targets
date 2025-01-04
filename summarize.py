import os
import sys
import math
import numpy as np
from scipy.spatial.transform import Rotation

cntrlPts = ["1104", "1105", "1106", "1107", "1111", "1112", "1113", "1114", "1115", "1116", "1120", "1121", "1122", "1123",
"1124", "1127", "1128", "1129", "1130", "1131", "1132", "1135", "1136", "1137", "1138", "1139", "1140", "1141", "1145", "1146",
"1148", "2002", "2004", "2005", "2006", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2017", "2018", "2019", "2020",
"2021", "2024", "2025", "2026", "2027", "2028", "2029", "2030", "2033", "2034", "2035", "2036"]



img_pos_1 = [80.70, 1749.60, 942.10]
img_pos_2 = [-2590.75, 523.95, 960.60]
img_pos_3 = [494.30, -2504.08, 1036.11]
img_pos_4 = [3723.10, -1359.74, 895.27]    

base_pose = Rotation.from_euler('zyx',[90,50,90],True)

#pose1 = Rotation.from_euler('zyx',[0 , 0, 0],True)
#pose2 = Rotation.from_euler('zyx',[0, 45, 0],True)
#pose3 = Rotation.from_euler('zyx',[0, 135, 0],True)
#pose4 = Rotation.from_euler('zyx',[0, 180, 0],True)
#pose5 = Rotation.from_euler('zyx',[0, 90, 0],True)
#pose2T = Rotation.from_euler('zyx',[0, -45, 0],True)
#pose3T = Rotation.from_euler('zyx',[0, -135, 0],True)
#pose4T = Rotation.from_euler('zyx',[0, -180, 0],True)
#pose5T = Rotation.from_euler('zyx',[0, -90, 0],True)

pose1 = [0 , 0, 0]
pose2 = [0, 45, 0]
pose3 = [0, 135, 0]
pose4 = [0, 180, 0]
pose5 = [0, 90, 0]
pose2T = [0, -45, 0]
pose3T = [0, -135, 0]
pose4T = [0, -180, 0]
pose5T = [0, -90, 0]


cam1Imgs = [1,2,9,10,17,18,25,26]
cam2Imgs = [3,4,11,12,19,20,27,28]
cam3Imgs = [5,6,13,14,21,22,29,30]
cam4Imgs = [7,8,15,16,23,24,31,32]


known_pts =[]
tie_pts = []

cntrlPts_w_3D_Coord = {}

cntrlPts_w_3D_Coord_list_frmt1 = []
cntrlPts_w_3D_Coord_list_frmt2 = []



def summarize(path):

    image_names = []

    observed_cntrl_pts_file = os.path.join(path,"observed_cntrl_pts.txt")
    with open(observed_cntrl_pts_file,'r') as observed_pts:
        for line in observed_pts:
            data = line.split('\t')
            entry = {}
            entry["x"]=data[1]
            entry["y"]=data[2]
            entry["z"]=data[3]
            cntrlPts_w_3D_Coord[data[0]] = entry

    files = os.listdir(path)
    
    for file in files:
        if file.startswith("."):
            if file.endswith("txt"):
                img_id = '_'.join(file.split(".")[1].split('_')[0:4])
                cntrlPts_w_3D_Coord_list_frmt1.append(f"{img_id}\n")
                with open(os.path.join(path,file),"r") as keypointsfile:
                    for line in keypointsfile:
                        data = line.split('\n')[0]
                        keypoint = data.split('\t')
                        if keypoint[0] in cntrlPts:
                            known_pts.append(data)
                            cntrl_pt_found = cntrlPts_w_3D_Coord[data.split('\t')[0]]
                            cntrlPts_w_3D_Coord_list_frmt1.append("\t".join([data.split('\t')[0],cntrl_pt_found["x"],cntrl_pt_found["y"],cntrl_pt_found["z"]]))
                            img_name_w_cntldpt_Str = "\t".join([
                                                     data.split('\t')[0],
                                                     '_'.join(file.split(".")[1].split('_')[0:4]),
                                                     cntrl_pt_found["x"],
                                                     cntrl_pt_found["y"],
                                                     cntrl_pt_found["z"] ])
                            
                            cntrlPts_w_3D_Coord_list_frmt2.append(f"{img_name_w_cntldpt_Str}")
                        else:
                            if data.split("\t")[0].endswith('png'):
                                print(breakpoint)
                            tie_pts.append(data)
        else:
            if file.endswith("png"):
                image_names.append(file.split('.')[0])

    all_keypoints = [None]*(len(known_pts)+len(tie_pts))
    all_keypoints[0:len(known_pts)-1] = known_pts
    all_keypoints[len(known_pts):-1] = tie_pts

    with open(os.path.join(path,"summarizedKeypoints.txt"),'w+') as summaryfile:
        for line in all_keypoints:
            summaryfile.write(f'{line}\n')

    with open(os.path.join(path,"observed_TIE_Pts.txt"),'w+') as tiepointsfile:
        count = 0
        setoftiepoints = set()
        for each in tie_pts:
            count+=1
            if each == '':
                continue

            tiept = each.split("\t")[0]
            if not tiept.endswith('png'):
                setoftiepoints.add(tiept)
            else:
                print("Breakpoint")


        for each_item in setoftiepoints:
            tiepointsfile.write(f'{each_item}\n')

    with open(os.path.join(path,"list_of_images.txt"),'w+') as listofimgs:
        image_names.sort()
        img_names_arr = np.array(image_names).reshape(-1,4)
        for each_row in img_names_arr:
            listofimgs.write(f'{each_row[0]}\t{each_row[1]}\t{each_row[2]}\t{each_row[3]}\n')

    with open(os.path.join(path,"list_cntrl_pts_in_each_img_fmt_1.txt"),'w+') as list_observedCntrlPts:
        for each in cntrlPts_w_3D_Coord_list_frmt1:
            list_observedCntrlPts.write(each)
    
    with open(os.path.join(path,"list_cntrl_pts_in_each_img_fmt_2.txt"),'w+') as list_observedCntrlPts:
        for each in cntrlPts_w_3D_Coord_list_frmt2:
            list_observedCntrlPts.write(each)

    with open(os.path.join(path,"image_EOPs.txt"), 'w+') as imageEops:
        for name in image_names:
            img_number = int(name.split('_')[1])
            cam_number = int(name.split('_')[-1])
            if (img_number >= 1) and (img_number<= 8):
                x = img_pos_1[0]
                y = img_pos_1[1]
                z = img_pos_1[2]

                if (img_number % 2 == 0): 
                    roll = Rotation.from_euler('zyx',[0, 0, -90],True)
                else:
                    roll = Rotation.from_euler('zyx',[0, 0, 0],True)

            elif (img_number >= 9) and (img_number<= 16):
                x = img_pos_2[0]
                y = img_pos_2[1]
                z = img_pos_2[2]

                if (img_number % 2 == 0): 
                    roll = Rotation.from_euler('zyx',[0, 0, -90],True)
                else:
                    roll = Rotation.from_euler('zyx',[0, 0, 0],True)

            elif (img_number >= 17) and (img_number<= 24):
                x = img_pos_3[0]
                y = img_pos_3[1]
                z = img_pos_3[2]

                if (img_number % 2 == 0): 
                    roll = Rotation.from_euler('zyx',[0, 0, -90],True)
                else:
                    roll = Rotation.from_euler('zyx',[0, 0, 0],True)

            elif (img_number >= 25) and (img_number<= 32):
                x = img_pos_4[0]
                y = img_pos_4[1]
                z = img_pos_4[2]

                if (img_number % 2 == 0): 
                    roll = Rotation.from_euler('zyx',[0, 0, -90],True)
                else:
                    roll = Rotation.from_euler('zyx',[0, 0, 0],True)

            [omega,phi,kappa] = np.dot(roll, base_pose).as_euler('zyx',True) 
            
            if (cam_number == 1):
                if (img_number in cam1Imgs):
                    [omega,phi,kappa] = [omega+pose1[0],phi+pose1[1],kappa + pose1[2]]
                elif (img_number in cam2Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose2T.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose2T[0], phi+pose2T[1], kappa+pose2T[2]] 
                elif (img_number in cam3Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose3T.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose3T[0], phi+pose3T[1], kappa+pose3T[2]]
                elif (img_number in cam4Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose4T.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose4T[0], phi+pose4T[1], kappa+pose4T[2]]
            elif (cam_number == 2):

                if (img_number in cam1Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose2.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose2[0], phi+pose2[1], kappa+pose2[2]] 
                elif (img_number in cam2Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose1.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose1[0], phi+pose1[1], kappa+pose1[2]] 
                elif (img_number in cam3Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose5T.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose5T[0], phi+pose5T[1], kappa+pose5T[2]] 
                elif (img_number in cam4Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose3T.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose3T[0], phi+pose3T[1], kappa+pose3T[2]] 

            elif (cam_number == 3):
                if (img_number in cam1Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose3.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose3[0], phi+pose3[1], kappa+pose3[2]]
                elif (img_number in cam2Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose5.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose5[0], phi+pose5[1], kappa+pose5[2]] 
                elif (img_number in cam3Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose1.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose1[0], phi+pose1[1], kappa+pose1[2]] 
                elif (img_number in cam4Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose2T.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose2T[0], phi+pose2T[1], kappa+pose2T[2]] 

            elif (cam_number == 3):
                if (img_number in cam1Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose4.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose4[0], phi+pose4[1], kappa+pose4[2]]
                elif (img_number in cam2Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose3.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose3[0], phi+pose3[1], kappa+pose3[2]] 
                elif (img_number in cam3Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose2.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose2[0], phi+pose2[1], kappa+pose2[2]]
                elif (img_number in cam4Imgs):
                    #[omega,phi,kappa] = Rotation.from_matrix(np.dot(np.dot(pose1.as_matrix(),roll.as_matrix()),base_pose.as_matrix())).as_euler('zyx',True)
                    [omega,phi,kappa] = [omega+pose1[0], phi+pose1[1], kappa+pose1[2]]
            



            #imageEops.write(f'{"_".join(name.split("_")[0:2])}\t{"_".join(name.split("_")[2:])}\t{x}\t{y}\t{z}\t{omega}\t{phi}\t{kappa}\n')
            imageEops.write(f'{name}\t{"_".join(name.split("_")[2:])}\t{x}\t{y}\t{z}\t{omega}\t{phi}\t{kappa}\n')





#def get_image_pose(filename, ):






if __name__=='__main__':
    path = sys.argv[1]
    summarize(path)