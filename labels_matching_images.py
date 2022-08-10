import os
import glob
import shutil

labels_path = glob.glob(os.path.join("./refine_plate_split/L1000_labels", "*.txt"))
images_path = glob.glob(os.path.join("./refine_plate_split/L1000", "*.jpg"))

os.makedirs("./refine_plate_split/L1000_images", exist_ok=True)
for label in labels_path:
    label_name = label.split('\\')[-1].split('.')[0]
    for image in images_path :
        image_name = image.split('\\')[-1].split('.')[0]
        if label_name == image_name:
            shutil.move(image, "./refine_plate_split/L1000_images/")
        else:
            continue