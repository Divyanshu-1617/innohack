import cv2
from ultralytics import YOLO

# ============================================================
# MODEL
# ============================================================

MODEL_PATH = r"D:\innohack\models\mot20_person_v1_best.pt"

model = YOLO(MODEL_PATH)

# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = r"D:\innohack\datasets\mot20\train\MOT20-01\img1\000001.jpg"

# ============================================================
# READ IMAGE
# ============================================================

frame = cv2.imread(IMAGE_PATH)

if frame is None:
    raise FileNotFoundError(
        f"Could not read image:\n{IMAGE_PATH}"
    )

# ============================================================
# YOLO DETECTION
# ============================================================

results = model.predict(
    source=frame,
    classes=[0],
    conf=0.15,
    imgsz=960,
    device=0,
    verbose=False
)

result = results[0]

# ============================================================
# COUNT PEOPLE
# ============================================================

person_count = 0

if result.boxes is not None:
    person_count = len(result.boxes)

print("=" * 60)
print("STEP 1 - YOLO PERSON MODEL TEST")
print("=" * 60)

print(f"Image       : {IMAGE_PATH}")
print(f"People found: {person_count}")

# ============================================================
# DRAW RESULTS
# ============================================================

annotated = result.plot()

# Resize display window
cv2.namedWindow(
    "YOLO Person Detection",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "YOLO Person Detection",
    1280,
    720
)

cv2.imshow(
    "YOLO Person Detection",
    annotated
)

print()
print("Press Q to close.")

while True:

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()