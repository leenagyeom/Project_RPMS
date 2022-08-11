import os
import glob

file_path = glob.glob(os.path.join("./refine_plate_split/ssibal", "*.txt"))
for file in file_path:
    f = open(file, 'r')
    read = f.read()
    split = read.split('\n')
    if len(split) < 8 :
        print(file)
print('삭제할 파일 갯수 :',len(file))

