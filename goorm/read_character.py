import os
import glob
from PIL import Image, ImageDraw
import pandas as pd

label_dict = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'가',
              11:'나', 12:'다', 13:'라', 14:'마', 15:'거', 16:'너', 17:'더', 18:'러', 19:'머', 20:'버',
              21:'서', 22:'어', 23:'저', 24:'고', 25:'노', 26:'도', 27:'로', 28:'모', 29:'보', 30:'소',
              31:'오', 32:'조', 33:'구', 34:'누', 35:'두', 36:'루', 37:'무', 38:'부', 39:'수', 40:'우',
              41:'주', 42:'아', 43:'바', 44:'사', 45:'자', 46:'배', 47:'허', 48:'하', 49:'호'}

def exp_path():
    origin_path = '/workspace/detection/yolov5/runs/detect'
    exp_path = os.listdir(origin_path)[-1]
    path = os.listdir(os.path.join(origin_path, exp_path))
    for file in path:
        if '.png' in file :
            img_file_path = os.path.join(origin_path, exp_path)
            image_file = file            
        else :
            txt_file_path = os.path.join(origin_path, exp_path, file)
            txt_file = os.listdir(txt_file_path)[0]
    return txt_file_path, img_file_path, image_file, txt_file


def listToString(str_list):
    result = ""
    for s in str_list:
        result += s
    return result.strip()


def txt_detect(list):
    plate_char_list = []
    pred_result = []
    for parts in list:
        label = parts[0]
        pred = parts[-1]
        plate = label_dict[label]
        plate_char_list.append(plate)
        pred_result.append(pred)
        
    plate_result = listToString(plate_char_list)

    return plate_result, pred_result
    
    
def sort_x_value(x):
    return x[1]


def image_coordinate():
    # 이미지 크기 224 * 65
    txt_path, img_path, img_file, txt_file = exp_path()
    image = Image.open(os.path.join(img_path, img_file))
    img_width, img_height = image.size

    bbox = []
    txt_sort = []
    with open(os.path.join(txt_path, txt_file), 'r') as f:
        data = f.readlines()
        for d in data :
            d = d.split(' ')
            w = float(d[3]) * img_width
            h = float(d[4]) * img_height
            x = float(d[1]) * img_width - (w / 2)
            y = float(d[2]) * img_height - (h / 2)
            bbox.append((x, y, w, h))
            txt_sort.append((int(d[0]), x, float(d[-1])))

        txt_sort.sort(key=sort_x_value)
        sort_plate_read, pred_result = txt_detect(txt_sort)
    return sort_plate_read, pred_result

        
if __name__ == "__main__":
    image_coordinate()