import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import DBSCAN

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
# ADAPTIVE ZONING SETTINGS
# ============================================================

DBSCAN_EPS = 150

# Minimum people required to create a crowd zone
MIN_PEOPLE = 3

# Padding around detected crowd
ZONE_PADDING = 50

# ============================================================
# PROCESS FRAMES
# ============================================================

for frame_number in range(1, 430):

    image_path = rf"{IMAGE_DIR}\{frame_number:06d}.jpg"

    frame = cv2.imread(image_path)

    if frame is None:
        continue

    # ========================================================
    # YOLO + BYTE TRACK
    # ========================================================

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

    # IMPORTANT:
    # Do NOT use result.plot()
    #
    # result.plot() creates all the giant person boxes,
    # IDs and confidence labels.
    #
    # Instead we start with the original frame.
    
    annotated = frame.copy()

    # ========================================================
    # COLLECT PERSON CENTERS
    # ========================================================

    centers = []

    if result.boxes is not None:

        for box in result.boxes:

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            centers.append([center_x, center_y])

    # ========================================================
    # DRAW SMALL PERSON POINTS
    # ========================================================

    # We show tiny points instead of boxes.
    # This lets us visually inspect what the clustering
    # algorithm is using without creating clutter.

    for center_x, center_y in centers:

        cv2.circle(
            annotated,
            (center_x, center_y),
            4,
            (255, 255, 255),
            -1
        )

    # ========================================================
    # ADAPTIVE CROWD CLUSTERING
    # ========================================================

    clusters = []

    if len(centers) >= MIN_PEOPLE:

        points = np.array(centers)

        clustering = DBSCAN(
            eps=DBSCAN_EPS,
            min_samples=MIN_PEOPLE
        ).fit(points)

        labels = clustering.labels_

        unique_labels = set(labels)

        for label in unique_labels:

            # -1 = noise / isolated person
            if label == -1:
                continue

            cluster_points = points[labels == label]

            if len(cluster_points) < MIN_PEOPLE:
                continue

            clusters.append(cluster_points)

    # ========================================================
    # SORT CLUSTERS
    # ========================================================

    # Largest crowd becomes Zone 1,
    # second largest becomes Zone 2, etc.

    clusters.sort(
        key=lambda cluster: len(cluster),
        reverse=True
    )

    # ========================================================
    # DRAW ADAPTIVE ZONES
    # ========================================================

    zone_number = 0

    # Semi-transparent overlay
    overlay = annotated.copy()

    for cluster in clusters:

        zone_number += 1

        people_count = len(cluster)

        # ----------------------------------------------------
        # Bounding rectangle around cluster
        # ----------------------------------------------------

        min_x = int(np.min(cluster[:, 0]))
        min_y = int(np.min(cluster[:, 1]))

        max_x = int(np.max(cluster[:, 0]))
        max_y = int(np.max(cluster[:, 1]))

        # Add padding
        min_x = max(0, min_x - ZONE_PADDING)
        min_y = max(0, min_y - ZONE_PADDING)

        max_x = min(
            frame.shape[1] - 1,
            max_x + ZONE_PADDING
        )

        max_y = min(
            frame.shape[0] - 1,
            max_y + ZONE_PADDING
        )

        # ----------------------------------------------------
        # Density calculation
        # ----------------------------------------------------

        zone_area = max(
            1,
            (max_x - min_x) * (max_y - min_y)
        )

        density = (
            people_count / zone_area
        ) * 100000

        # ----------------------------------------------------
        # Risk level
        # ----------------------------------------------------

        if density >= 12:

            risk = "HIGH"

            # Red
            zone_color = (0, 0, 255)

        elif density >= 5:

            risk = "MEDIUM"

            # Orange
            zone_color = (0, 165, 255)

        else:

            risk = "LOW"

            # Green
            zone_color = (0, 200, 0)

        # ----------------------------------------------------
        # Draw transparent zone
        # ----------------------------------------------------

        cv2.rectangle(
            overlay,
            (min_x, min_y),
            (max_x, max_y),
            zone_color,
            -1
        )

        # ----------------------------------------------------
        # Draw zone border
        # ----------------------------------------------------

        cv2.rectangle(
            annotated,
            (min_x, min_y),
            (max_x, max_y),
            zone_color,
            4
        )

        # ----------------------------------------------------
        # Zone title
        # ----------------------------------------------------

        title = (
            f"ZONE {zone_number} | "
            f"{people_count} PEOPLE | "
            f"{risk}"
        )

        # Position title above zone
        title_y = max(30, min_y - 10)

        # Background for text
        (text_width, text_height), _ = cv2.getTextSize(
            title,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            2
        )

        cv2.rectangle(
            annotated,
            (min_x, title_y - text_height - 12),
            (min_x + text_width + 12, title_y + 5),
            zone_color,
            -1
        )

        # Text
        cv2.putText(
            annotated,
            title,
            (min_x + 6, title_y - 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        # ----------------------------------------------------
        # Density text
        # ----------------------------------------------------

        density_text = f"Density: {density:.2f}"

        cv2.putText(
            annotated,
            density_text,
            (min_x + 10, min_y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

    # ========================================================
    # APPLY TRANSPARENT ZONE OVERLAY
    # ========================================================

    annotated = cv2.addWeighted(
        overlay,
        0.18,
        annotated,
        0.82,
        0
    )

    # ========================================================
    # REDRAW ZONE BORDERS AFTER OVERLAY
    # ========================================================

    for index, cluster in enumerate(clusters):

        min_x = int(np.min(cluster[:, 0]))
        min_y = int(np.min(cluster[:, 1]))

        max_x = int(np.max(cluster[:, 0]))
        max_y = int(np.max(cluster[:, 1]))

        min_x = max(0, min_x - ZONE_PADDING)
        min_y = max(0, min_y - ZONE_PADDING)

        max_x = min(
            frame.shape[1] - 1,
            max_x + ZONE_PADDING
        )

        max_y = min(
            frame.shape[0] - 1,
            max_y + ZONE_PADDING
        )

        people_count = len(cluster)

        zone_area = max(
            1,
            (max_x - min_x) * (max_y - min_y)
        )

        density = (
            people_count / zone_area
        ) * 100000

        if density >= 12:
            zone_color = (0, 0, 255)

        elif density >= 5:
            zone_color = (0, 165, 255)

        else:
            zone_color = (0, 200, 0)

        cv2.rectangle(
            annotated,
            (min_x, min_y),
            (max_x, max_y),
            zone_color,
            4
        )

    # ========================================================
    # TOP INFORMATION PANEL
    # ========================================================

    total_people = len(centers)

    panel_height = 110

    cv2.rectangle(
        annotated,
        (10, 10),
        (390, panel_height),
        (20, 20, 20),
        -1
    )

    cv2.putText(
        annotated,
        "AI CROWD MANAGEMENT",
        (25, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated,
        f"People Detected: {total_people}",
        (25, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated,
        f"Adaptive Zones: {zone_number}",
        (25, 98),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.namedWindow(
        "Adaptive Crowd Density",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "Adaptive Crowd Density",
        1280,
        720
    )

    cv2.imshow(
        "Adaptive Crowd Density",
        annotated
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()