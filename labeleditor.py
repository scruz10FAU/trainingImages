import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

# Config
image_dir = 'trainImages/images'
label_dir = 'trainImages/labels'
class_id = 0  # default class for all boxes

#bad_images = ['img2280.jpg', 'img2290.jpg', 'img2300.jpg', 'img2310.jpg']
image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))])
#image_files = [fname for fname in bad_images]
print(image_files)
index = 0
boxes = []
 
# === GUI SETUP ===
root = tk.Tk()
root.title("YOLO Label Editor (Mouse Drawing)")

canvas_width, canvas_height = 640, 480
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, cursor="tcross")
canvas.pack()

img_tk = None
start_x = start_y = 0
rect = None

# === FUNCTIONS ===

def load_image(idx):
    global img_tk, boxes
    boxes = []
    canvas.delete("all")
    
    img_path = os.path.join(image_dir, image_files[idx])
    image = Image.open(img_path)
    image = image.resize((canvas_width, canvas_height))
    img_tk = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    
    # Load existing boxes if label exists
    name = os.path.splitext(image_files[idx])[0]
    label_path = os.path.join(label_dir, f"{name}.txt")
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls, x, y, w, h = map(float, parts)
                    draw_saved_box(x, y, w, h)

def draw_saved_box(xc, yc, w, h):
    x1 = (xc - w / 2) * canvas_width
    y1 = (yc - h / 2) * canvas_height
    x2 = (xc + w / 2) * canvas_width
    y2 = (yc + h / 2) * canvas_height
    canvas_id = canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
    boxes.append((class_id, xc, yc, w, h, canvas_id))

def on_mouse_down(event):
    global start_x, start_y, rect
    start_x, start_y = event.x, event.y
    rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

def on_mouse_drag(event):
    canvas.coords(rect, start_x, start_y, event.x, event.y)

def on_mouse_up(event):
    global boxes
    x1, y1 = start_x, start_y
    x2, y2 = event.x, event.y
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
        # Check for box click (delete mode)
        to_delete = None
        for box in boxes:
            cx = box[1] * canvas_width
            cy = box[2] * canvas_height
            bw = box[3] * canvas_width / 2
            bh = box[4] * canvas_height / 2
            if x1 > cx - bw and x1 < cx + bw and y1 > cy - bh and y1 < cy + bh:
                to_delete = box
                break
        if to_delete:
            canvas.delete(to_delete[5])
            boxes.remove(to_delete)
            return
    # Otherwise: add box
    w = (x2 - x1) / canvas_width
    h = (y2 - y1) / canvas_height
    xc = (x1 + x2) / 2 / canvas_width
    yc = (y1 + y2) / 2 / canvas_height
    canvas_id = canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
    boxes.append((class_id, xc, yc, w, h, canvas_id))

def save_label():
    name = os.path.splitext(image_files[index])[0]
    label_path = os.path.join(label_dir, f"{name}.txt")
    with open(label_path, 'w') as f:
        for box in boxes:
            f.write(f"{box[0]} {box[1]:.6f} {box[2]:.6f} {box[3]:.6f} {box[4]:.6f}\n")
def next_image():
    global index
    save_label()
    if index < len(image_files) - 1:
        index += 1
        load_image(index)

def prev_image():
    global index
    save_label()
    if index > 0:
        index -= 1
        load_image(index)

def clear_boxes():
    global boxes
    # Remove rectangles from the canvas
    for box in boxes:
        canvas.delete(box[5])
    boxes = []

    # Remove the corresponding label file
    name = os.path.splitext(image_files[index])[0]
    label_path = os.path.join(label_dir, f"{name}.txt")
    if os.path.exists(label_path):
        os.remove(label_path)


# === BUTTONS ===
btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="◀ Prev", command=prev_image).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Clear Boxes", command=clear_boxes).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Next ▶", command=next_image).pack(side=tk.LEFT)
btn_frame.pack(pady=5)

canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_drag)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# === START ===
load_image(index)
root.mainloop()