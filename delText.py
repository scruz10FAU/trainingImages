import os

# Set the paths
image_folder = "testImages/images"
text_folder = "testImages/labels"

# Define valid image extensions
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

# Get base names of all image files
image_basenames = {
    os.path.splitext(f)[0]
    for f in os.listdir(image_folder)
    if os.path.splitext(f)[1].lower() in image_extensions
}

# Loop through .txt files and delete if no matching image
for f in os.listdir(text_folder):
    name, ext = os.path.splitext(f)
    if ext.lower() == '.txt' and name not in image_basenames:
        txt_path = os.path.join(text_folder, f)
        print(f"Deleting {f} – no matching image found in {image_folder}.")
        os.remove(txt_path)
