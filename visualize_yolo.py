import cv2
import os

IMAGE_DIR = r"D:\innohack\datasets\mot20_person_yolo\images\train"
LABEL_DIR = r"D:\innohack\datasets\mot20_person_yolo\labels\train"

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

image_name = "000001.jpg"

image_path = os.path.join(IMAGE_DIR, image_name)
label_path = os.path.join(
    LABEL_DIR,
    os.path.splitext(image_name)[0] + ".txt"
)

frame = cv2.imread(image_path)

if frame is None:
    raise RuntimeError(f"Could not read image: {image_path}")

with open(label_path, "r") as f:
    for line in f:
        parts = line.strip().split()

        if len(parts) != 5:
            continue

        class_id, xc, yc, w, h = map(float, parts)

        # YOLO normalized coordinates -> pixel coordinates
        x_center = xc * IMAGE_WIDTH
        y_center = yc * IMAGE_HEIGHT
        box_width = w * IMAGE_WIDTH
        box_height = h * IMAGE_HEIGHT

        x1 = int(x_center - box_width / 2)
        y1 = int(y_center - box_height / 2)
        x2 = int(x_center + box_width / 2)
        y2 = int(y_center + box_height / 2)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "person",
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

cv2.imshow("MOT20 -> YOLO Ground Truth", frame)

print("Press any key to close.")

cv2.waitKey(0)
cv2.destroyAllWindows()