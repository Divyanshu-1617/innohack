import cv2
from ultralytics import YOLO

# ============================================================
# MODEL
# ============================================================

MODEL_PATH = r"D:\innohack\runs\detect\mot20_person_v1\weights\best.pt"

model = YOLO(MODEL_PATH)

# ============================================================
# CCTV IMAGE SEQUENCE
# ============================================================

IMAGE_DIR = r"D:\innohack\datasets\mot20\train\MOT20-01\img1"

# ============================================================
# PROCESS VIDEO
# ============================================================

for frame_number in range(1, 430):

    image_path = rf"{IMAGE_DIR}\{frame_number:06d}.jpg"

    frame = cv2.imread(image_path)

    if frame is None:
        print(f"Could not read frame {frame_number}")
        continue

    # YOLO + ByteTrack
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

    # Draw detections + tracking IDs
    annotated_frame = result.plot()

    # Count people
    people_count = len(result.boxes)

    # Display count
    cv2.putText(
        annotated_frame,
        f"People: {people_count}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3
    )

    # Display frame number
    cv2.putText(
        annotated_frame,
        f"Frame: {frame_number}",
        (20, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    # Resizable window
    cv2.namedWindow(
        "CCTV Crowd Tracking",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "CCTV Crowd Tracking",
        1280,
        720
    )

    cv2.imshow(
        "CCTV Crowd Tracking",
        annotated_frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()