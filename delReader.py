import os

# Set these paths
image_folder = 'trainText/images'
text_file_path = 'trainText/full_list.txt'

# Get current (remaining) image filenames in the folder
remaining_images = set(os.listdir(image_folder))

# Clean the text file based on remaining images
new_lines = []
with open(text_file_path, 'r') as f:
    for line in f:
        # Assume filename is the first word in the line
        filename = line.split()[0]
        if filename in remaining_images:
            new_lines.append(line)

# Overwrite the original file with the filtered lines
print(new_lines)
with open(text_file_path, 'w') as f:
    f.writelines(new_lines)

print(f"Cleaned up {text_file_path}: kept {len(new_lines)} lines.")
