import os
import random
import shutil
import glob
import numpy as np

random.seed(6146)

origin_tdata_path = "./refine_plate_split/"
t_dir = sorted(os.listdir(origin_tdata_path))

lng_dir = "./L1000"
kbr_dir = "./K1000"
pne_dir = "./P1000"
jsw_dir = "./J1000"

os.makedirs(lng_dir, exist_ok=True)
os.makedirs(kbr_dir, exist_ok=True)
os.makedirs(pne_dir, exist_ok=True)
os.makedirs(jsw_dir, exist_ok=True)

for i in t_dir:
    data_len = len(glob.glob(os.path.join(origin_tdata_path, "*.jpg")))
    rfile_list1 = np.array(t_dir)

    lng_data = random.sample(range(data_len), int(data_len * 0.25))
    lng_data_list = []
    for i in lng_data:
        lng_data_list.append(rfile_list1[i])

    rfile_list2 = [x for x in rfile_list1 if x not in lng_data_list]

    kbr_data = random.sample(range(len(rfile_list2)), int(len(rfile_list2) * 0.333))
    kbr_data_list = []
    for i in kbr_data:
        kbr_data_list.append(rfile_list2[i])

    rfile_list3 = [x for x in rfile_list2 if x not in kbr_data_list]

    jsw_data = random.sample(range(len(rfile_list3)), int(len(rfile_list3) * 0.5))
    jsw_data_list = []
    for i in jsw_data:
        jsw_data_list.append(rfile_list3[i])

    rfile_list4 = [x for x in rfile_list3 if x not in jsw_data_list]

    pne_data = random.sample(range(len(rfile_list4)), int(len(rfile_list4)))
    pne_data_list = []
    for i in pne_data:
        pne_data_list.append(rfile_list4[i])

    for l, k, j, p in zip(lng_data_list, kbr_data_list, jsw_data_list, pne_data_list):
        shutil.move(origin_tdata_path+l, lng_dir)
        shutil.move(origin_tdata_path+k, kbr_dir)
        shutil.move(origin_tdata_path+j, jsw_dir)
        shutil.move(origin_tdata_path+p, pne_dir)