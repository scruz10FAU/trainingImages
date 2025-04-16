import os
from PIL import Image
import imagehash

# Folder containing the images
folder_path = "testImages/images"

# Hash dictionary
hashes = {}
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        file_path = os.path.join(folder_path, filename)
        try:
            with Image.open(file_path) as img:
                hash = imagehash.phash(img)
                if hash in hashes:
                    print(f"Duplicate found: {filename} is similar to {hashes[hash]}")
                    os.remove(file_path)
                else:
                    hashes[hash] = filename
        except Exception as e:
            print(f"Error processing {filename}: {e}")
