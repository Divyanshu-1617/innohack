import cv2
from ultralytics import YOLO

# Load pretrained YOLO model
model = YOLO("yolo11n.pt")

# Phone camera stream
url = "http://10.152.252.81:8080/video"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Could not connect to phone camera")
    exit()

print("Connected to phone camera!")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to receive frame")
        break

    # YOLO detection - ONLY PERSON (class 0)
    results = model(
        frame,
        classes=[0],
        conf=0.10,
        imgsz=800,
        verbose=False
    )

    # Draw detections
    annotated_frame = results[0].plot()

    # Number of detected people
    people_count = len(results[0].boxes)

    cv2.putText(
        annotated_frame,
        f"People: {people_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Crowd Management - Person Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()