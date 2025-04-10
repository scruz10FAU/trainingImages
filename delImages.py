import os
import random

# Path to your folder
folder_path = 'trainText/images'
#label_path = 'trainImages/labels'

# Get all image filenames
image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
#label_files = sorted([f for f in os.listdir(label_path) if f.lower().endswith(('.txt'))])

total = len(image_files)
keep_count = int(total * 0.10)
spacing = total // keep_count

# Get the images to keep (evenly spaced)
images_to_keep = set(image_files[i] for i in range(0, total, spacing))
#files_to_keep = set(label_files[i] for i in range(0, total, spacing))

# Delete everything else
deleted = 0
for idx, f in enumerate(image_files):
    if f not in images_to_keep:
        #print(f"Removed: {os.path.join(folder_path, f)}")
        #print(f"Removed: {os.path.join(label_path, label_files[idx])}")
        os.remove(os.path.join(folder_path, f))
        #os.remove(os.path.join(label_path, label_files[idx]))
        deleted += 1

print(f"Deleted {deleted} images. Kept {len(images_to_keep)}.")
