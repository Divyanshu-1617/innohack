import cv2
from ultralytics import YOLO

# ============================================================
# MODEL
# ============================================================

MODEL_PATH = r"D:\innohack\runs\detect\mot20_person_v1\weights\best.pt"

model = YOLO(MODEL_PATH)

# ============================================================
# CCTV SEQUENCE
# ============================================================

IMAGE_DIR = r"D:\innohack\datasets\mot20\train\MOT20-01\img1"

# ============================================================
# ZONES
#
# Coordinates are based on the 1920x1080 image.
# We'll adjust these after seeing the actual camera view.
# ============================================================

ZONES = {
    "A": (0, 0, 960, 540),
    "B": (960, 0, 1920, 540),
    "C": (0, 540, 960, 1080),
    "D": (960, 540, 1920, 1080),
}

# ============================================================
# PROCESS FRAMES
# ============================================================

for frame_number in range(1, 430):

    image_path = rf"{IMAGE_DIR}\{frame_number:06d}.jpg"

    frame = cv2.imread(image_path)

    if frame is None:
        continue

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[0],
        conf=0.15,
        imgsz=960,
        device=0,
        verbose=False
    )

    result = results[0]

    annotated = result.plot()

    # ========================================================
    # COUNT PEOPLE IN EACH ZONE
    # ========================================================

    zone_counts = {
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0
    }

    if result.boxes is not None:

        for box in result.boxes:

            # xyxy = x1, y1, x2, y2
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            # Center of person bounding box
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            # Find zone
            for zone_name, (zx1, zy1, zx2, zy2) in ZONES.items():

                if (
                    zx1 <= center_x <= zx2
                    and
                    zy1 <= center_y <= zy2
                ):
                    zone_counts[zone_name] += 1
                    break

    # ========================================================
    # DRAW ZONES
    # ========================================================

    for zone_name, (x1, y1, x2, y2) in ZONES.items():

        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated,
            f"Zone {zone_name}: {zone_counts[zone_name]}",
            (x1 + 20, y1 + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

    # ========================================================
    # TOTAL PEOPLE
    # ========================================================

    total_people = sum(zone_counts.values())

    cv2.putText(
        annotated,
        f"TOTAL PEOPLE: {total_people}",
        (20, 1040),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.namedWindow(
        "Crowd Density",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "Crowd Density",
        1280,
        720
    )

    cv2.imshow(
        "Crowd Density",
        annotated
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()