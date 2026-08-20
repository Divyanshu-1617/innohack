import os
import shutil
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================

MOT_SEQUENCE = r"D:\innohack\datasets\MOT20\train\MOT20-01"

OUTPUT_DIR = r"D:\innohack\datasets\mot20_person_yolo"

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# First 80% of frames -> train
# Last 20% -> validation
TRAIN_RATIO = 0.8


# ============================================================
# PATHS
# ============================================================

IMAGE_DIR = os.path.join(MOT_SEQUENCE, "img1")
GT_FILE = os.path.join(MOT_SEQUENCE, "gt", "gt.txt")

TRAIN_IMAGE_DIR = os.path.join(OUTPUT_DIR, "images", "train")
VAL_IMAGE_DIR = os.path.join(OUTPUT_DIR, "images", "val")

TRAIN_LABEL_DIR = os.path.join(OUTPUT_DIR, "labels", "train")
VAL_LABEL_DIR = os.path.join(OUTPUT_DIR, "labels", "val")


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

for directory in [
    TRAIN_IMAGE_DIR,
    VAL_IMAGE_DIR,
    TRAIN_LABEL_DIR,
    VAL_LABEL_DIR,
]:
    os.makedirs(directory, exist_ok=True)


# ============================================================
# READ GROUND TRUTH
# ============================================================

if not os.path.exists(GT_FILE):
    raise FileNotFoundError(f"Ground truth not found: {GT_FILE}")

annotations = defaultdict(list)

with open(GT_FILE, "r") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split(",")

        if len(parts) < 6:
            continue

        frame_id = int(parts[0])

        # MOT format:
        # frame, id, x, y, width, height, mark, class, visibility

        gt_class = int(parts[7])

        # Keep ONLY normal pedestrians.
        # Other MOT classes may represent things such as
        # non-pedestrian/static/distractor annotations.
        if gt_class != 1:
                continue

        x = float(parts[2])
        y = float(parts[3])
        width = float(parts[4])
        height = float(parts[5])

        # Ignore invalid bounding boxes
        if width <= 0 or height <= 0:
            continue

        # Ignore boxes completely outside image
        if x + width <= 0 or y + height <= 0:
            continue

        # Clip bounding box to image boundaries
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(IMAGE_WIDTH, x + width)
        y2 = min(IMAGE_HEIGHT, y + height)

        clipped_width = x2 - x1
        clipped_height = y2 - y1

        if clipped_width <= 0 or clipped_height <= 0:
            continue

        # Convert to YOLO normalized format
        x_center = (x1 + x2) / 2 / IMAGE_WIDTH
        y_center = (y1 + y2) / 2 / IMAGE_HEIGHT

        norm_width = clipped_width / IMAGE_WIDTH
        norm_height = clipped_height / IMAGE_HEIGHT

        # Class 0 = person
        annotations[frame_id].append(
            f"0 {x_center:.6f} {y_center:.6f} "
            f"{norm_width:.6f} {norm_height:.6f}"
        )


# ============================================================
# FIND FRAMES
# ============================================================

image_files = [
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

image_files.sort()

if not image_files:
    raise RuntimeError("No images found.")

total_frames = len(image_files)

train_frames = int(total_frames * TRAIN_RATIO)

print("=" * 60)
print("MOT20 -> YOLO PERSON DATASET")
print("=" * 60)

print(f"Total images: {total_frames}")
print(f"Training images: {train_frames}")
print(f"Validation images: {total_frames - train_frames}")
print(f"Annotated frames: {len(annotations)}")


# ============================================================
# PROCESS IMAGES
# ============================================================

for index, image_name in enumerate(image_files):

    frame_id = int(os.path.splitext(image_name)[0])

    source_image = os.path.join(IMAGE_DIR, image_name)

    if index < train_frames:
        image_output_dir = TRAIN_IMAGE_DIR
        label_output_dir = TRAIN_LABEL_DIR
    else:
        image_output_dir = VAL_IMAGE_DIR
        label_output_dir = VAL_LABEL_DIR

    destination_image = os.path.join(
        image_output_dir,
        image_name
    )

    destination_label = os.path.join(
        label_output_dir,
        os.path.splitext(image_name)[0] + ".txt"
    )

    # Copy image
    shutil.copy2(
        source_image,
        destination_image
    )

    # Write YOLO labels
    with open(destination_label, "w") as label_file:

        for annotation in annotations.get(frame_id, []):
            label_file.write(annotation + "\n")


# ============================================================
# CREATE data.yaml
# ============================================================

yaml_path = os.path.join(
    OUTPUT_DIR,
    "data.yaml"
)

with open(yaml_path, "w") as f:
    f.write(
        f"""path: {OUTPUT_DIR.replace(chr(92), "/")}
train: images/train
val: images/val

names:
  0: person
"""
    )


# ============================================================
# SUMMARY
# ============================================================

train_labels = len(os.listdir(TRAIN_LABEL_DIR))
val_labels = len(os.listdir(VAL_LABEL_DIR))

print()
print("=" * 60)
print("CONVERSION COMPLETE")
print("=" * 60)

print(f"Training images : {len(os.listdir(TRAIN_IMAGE_DIR))}")
print(f"Validation images: {len(os.listdir(VAL_IMAGE_DIR))}")
print(f"Training labels : {train_labels}")
print(f"Validation labels: {val_labels}")

print()
print(f"Dataset created at:")
print(OUTPUT_DIR)

print()
print("data.yaml:")
print(yaml_path)