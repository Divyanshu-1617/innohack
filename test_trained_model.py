import cv2
from ultralytics import YOLO

# Fine-tuned model
MODEL_PATH = r"D:\innohack\runs\detect\mot20_person_v1\weights\best.pt"

# MOT20 test image
IMAGE_PATH = r"D:\innohack\datasets\mot20\train\MOT20-01\img1\000001.jpg"

# Load model
model = YOLO(MODEL_PATH)

# Run detection
results = model(
    IMAGE_PATH,
    classes=[0],
    conf=0.15,
    imgsz=960,
    device=0,
    verbose=False
)

result = results[0]

# Draw detections
annotated = result.plot()

# Count detected people
people_count = len(result.boxes)

print("People detected:", people_count)

# Save full-resolution result
OUTPUT_PATH = r"D:\innohack\test_result.jpg"

cv2.imwrite(OUTPUT_PATH, annotated)

print("Saved result to:")
print(OUTPUT_PATH)

# Display resized window
cv2.namedWindow(
    "Fine-Tuned MOT20 Person Detector",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Fine-Tuned MOT20 Person Detector",
    1280,
    720
)

cv2.imshow(
    "Fine-Tuned MOT20 Person Detector",
    annotated
)

cv2.waitKey(0)
cv2.destroyAllWindows()
