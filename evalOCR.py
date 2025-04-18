from paddleocr import PaddleOCR
import os
import matplotlib.pyplot as plt
import cv2
import math
from PIL import Image
import numpy as np
from difflib import SequenceMatcher
import statistics
import random

# ── CONFIG ────────────────────────────────────────────────────────────────
label_list_file = "./train_list.txt"
use_gpu      = False   # True if you have a GPU available
# ──────────────────────────────────────────────────────────────────────────

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=False, 
                use_gpu=False,
                det_model_dir=None,
                rec_model_dir='C:/Users/SGarcia/Desktop/trainingImages/en_rec_custom',
                lang='en'
                )


BLUR_THRESH = 1000
RES_THRESH = 3900

def print_stats(data, metrics="Metrics"):
    print(metrics)
    rmean = statistics.mean(data)
    rmed = statistics.median(data)
    rmode = statistics.mode(data)
    print(f"Mean: {rmean:2f}, Median: {rmed:2f}, Mode: {rmode:2f}")

def blur_score(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score

def get_res(img):
    h, w = img.shape[:2]
    return h*w

def similarity_pct(a, b):
    return SequenceMatcher(None, a, b).ratio() * 100

def print_table(data):
    col_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]
    # print each row
    for row in data:
        print(" | ".join(f"{str(val):{col_widths[i]}}" for i, val in enumerate(row)))

def upscale_img(image):
        
    #convert to numpy format
    img_np = cv2.imread(image)
    
    
        
    #Load image (license plate region ideally)

    #Create the DNN super-res object
    sr = cv2.dnn_superres.DnnSuperResImpl_create()

    #Load the ESPCN model
    model_path = "C:/Users/SGarcia/Desktop/trainingImages/ESPCN_x4.pb"
    sr.readModel(model_path)
    sr.setModel("espcn", 4)  # Model name and scale

    #Run super-resolution
    upscaled = sr.upsample(img_np)
    #cv2.imshow("upscaled", upscaled)
    #sr_np = np.array(sr_image)
    #sr_cv2_image = cv2.cvtColor(sr_np, cv2.COLOR_RGB2BGR)

    #return the result
    return upscaled

# Buckets & counters
buckets = {
    'clear':      {'correct':0, 'incorrect':0, 'no_det':0, 'sim_sum':0, 'count':0},
    'blurry':     {'correct':0, 'incorrect':0, 'no_det':0, 'sim_sum':0, 'count':0},
}

failed_clear = []
failed_blurry = []
blur_list = []
failed_all = [["img path", "true text", "predicted text", "blur score", "Resolution"]]
passed_all = [["img path", "true text", "predicted text", "blur score", "Resolution"]]
undetected_all = [["img path", "true text", "predicted text", "blur score", "Resolution"]]
res_list = []
exclude_text = []
state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
for state in state_names:
    exclude_text.append(state.upper().strip())
common_text = ["MYFLORIDA", "SUNSHINESTATE", "EMPIRESTATE", "GRANDCANYONSTATE", "EMERGENCYMEDICALSERVICES"]
for text in common_text:
    exclude_text.append(text.upper().strip())

with open(label_list_file, "r", encoding="utf-8") as f:
    for line in f:
        img_rel, gt_text = line.strip().split(maxsplit=1)
        img_path = (
            img_rel
            if os.path.isabs(img_rel)
            #else os.path.join(os.path.dirname(label_list_file), "images", img_rel)
            else os.path.join(os.path.dirname(label_list_file), img_rel)
        )

        # 0) Load original image for blur check (and later display)
        orig = cv2.imread(img_path)
        if orig is None:
            print(f"Could not open {img_path}, skipping")
            continue
        up = upscale_img(img_path)
        blur = blur_score(orig)
        res = get_res(orig)
        blur_list.append(blur)
        res_list.append(res)
        is_blurry = blur < BLUR_THRESH or res < RES_THRESH
        key = 'blurry' if is_blurry else 'clear'
        buckets[key]['count'] += 1

        # 1) Optionally upscale
        # (keep your existing upscale_img if desired, else skip)
        # up = upscale_img(img_path)

        # 2) Run OCR
        ocr_out = ocr.ocr(up, cls=False)
        preds = []
        for page in ocr_out:
            if page is not None:
                for line in page:
                    cline = line[1][0].upper().strip()
                    if cline not in exclude_text:
                        preds.append(line[1][0])
        pred_text = "".join(preds).strip()

        # 3) Compute similarity and category
        sim = similarity_pct(gt_text, pred_text)
        buckets[key]['sim_sum'] += sim

        if not preds:
            buckets[key]['no_det'] += 1
            failed_blur_list = failed_blurry if key=='blurry' else failed_clear
            failed_blur_list.append((img_path, "(no det)", gt_text, blur, res))
            undetected_all.append([img_path, gt_text, "", blur, res])
        elif pred_text == gt_text:
            buckets[key]['correct'] += 1
            passed_all.append([img_path, gt_text, pred_text, blur, res])
        else:
            buckets[key]['incorrect'] += 1
            failed_blur_list = failed_blurry if key=='blurry' else failed_clear
            failed_blur_list.append((img_path, pred_text, gt_text, blur, res))
            failed_all.append([img_path, gt_text, pred_text, blur, res])

# 4) Reporting
# 5) Combined bar chart + inline report
labels     = ['clear','blurry']
corrects   = [buckets[k]['correct']   for k in labels]
incorrects = [buckets[k]['incorrect'] for k in labels]
nos        = [buckets[k]['no_det']    for k in labels]

x     = np.arange(len(labels))
width = 0.25

fig, ax = plt.subplots(figsize=(6,4))
ax.bar(  x - width, corrects,   width, label='Correct')
ax.bar(  x,         incorrects, width, label='Incorrect')
ax.bar(  x + width, nos,       width, label='No Detection')

ax.set_xticks(x)
ax.set_xticklabels([l.title() for l in labels])
ax.set_ylabel("Image Count")
ax.set_title("OCR Performance by Blur vs. Clear")
ax.legend()

# Make room at the bottom for text
plt.subplots_adjust(bottom=0.25)

# Build the report string
report_lines = []
for key in labels:
    b = buckets[key]
    if b['count']==0: continue
    acc    = b['correct']/b['count']*100
    no_det = b['no_det']   /b['count']*100
    avg_sim= b['sim_sum']  /b['count']
    report_lines.append(
        f"{key.title()} ({b['count']}):  Acc={acc:.1f}%  No‑det={no_det:.1f}%  AvgSim={avg_sim:.1f}%"
    )

report_str = "\n".join(report_lines)

# Draw it under the axes, in figure coordinates (0–1)
fig.text(
    0.5,           # x position (centered)
    0.02,          # y position just above the bottom of the figure
    report_str,
    ha='center',   # center horizontally
    va='bottom',   # anchor text at its bottom
    fontsize=9
)

plt.show()

print("Not detected")
print_table(undetected_all)
print("Failed")
print_table(failed_all)
print("Passed")
print_table(passed_all)

print_stats(res_list, "Resolution Metrics")
print_stats(blur_list, "Blur Metrics")


# 6) Optional: collage of first few failures in each bucket
def show_collage(failed_list, title):
    n = min(len(failed_list), 9)
    failed_list = random.sample(failed_list, n)
    cols = 3; rows = math.ceil(n/cols)
    fig, axs = plt.subplots(rows, cols, figsize=(4*cols,3*rows))
    for ax,(p,pred,gt,blur,res) in zip(axs.flatten(), failed_list[:n]):
        img = cv2.imread(p)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ax.imshow(img)
        ax.set_title(f"Path:{p}\nPred:{pred}/GT:{gt}\nblur:{blur:.0f}/res:{res}", fontsize=8)
        ax.axis('off')
    for ax in axs.flatten()[n:]:
        ax.axis('off')
    fig.suptitle(title)
    plt.tight_layout()
    plt.show()

show_collage(failed_clear, "Clear Images — Failures")
show_collage(failed_blurry, "Blurry Images — Failures")