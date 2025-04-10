import os
import math
from pathlib import Path
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

# Settings
img_dir = Path('trainImages/images')
label_dir = Path('trainImages/labels')
cols = 4
rows = 4
batch_size = cols * rows

# Get all image files
image_files = sorted([f for f in img_dir.glob("*.*") if f.suffix.lower() in ['.jpg', '.png']])
total_images = len(image_files)
total_batches = math.ceil(total_images / batch_size)

print(f"📦 Total images: {total_images} | Batches: {total_batches}")

for i in range(8, total_batches):
    # Choose which batch to view
    current_batch = i  # 🔁 Change this to 1, 2, 3... to see next grid

    # Get images for this batch
    start = current_batch * batch_size
    end = min(start + batch_size, total_images)
    batch_files = image_files[start:end]

    # Plot
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
    fig.canvas.manager.set_window_title(f"Image Grid - Batch {i + 1} of {total_batches}")

    axes = axes.flatten()

    for ax, img_path in zip(axes, batch_files):
        label_path = label_dir / img_path.with_suffix('.txt').name
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        cls, x, y, bw, bh = map(float, parts)
                        x1 = (x - bw / 2) * w
                        y1 = (y - bh / 2) * h
                        x2 = (x + bw / 2) * w
                        y2 = (y + bh / 2) * h
                        draw.rectangle([x1, y1, x2, y2], outline='blue', width=4)

        ax.imshow(img)
        ax.set_title(img_path.name, fontsize=8)
        ax.axis('off')

    # Hide unused tiles
    for ax in axes[len(batch_files):]:
        ax.axis('off')

    plt.tight_layout()
    plt.show()