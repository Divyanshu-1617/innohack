import numpy as np
from ultralytics import YOLO
from sklearn.cluster import DBSCAN


MODEL_PATH = r"D:\innohack\runs\detect\mot20_person_v1\weights\best.pt"

DBSCAN_EPS = 150
MIN_PEOPLE = 3
PADDING = 40


class DetectionService:

    def __init__(self):
        self.model = YOLO(MODEL_PATH)

    def analyze(self, frame):

        # YOLO + ByteTrack
        results = self.model.track(
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

        people = []
        centers = []

        # -----------------------------
        # PERSON DETECTION
        # -----------------------------

        if result.boxes is not None:

            for box in result.boxes:

                x1, y1, x2, y2 = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                )

                confidence = float(
                    box.conf[0].cpu().numpy()
                )

                # Bottom-center / foot point
                center_x = int((x1 + x2) / 2)
                center_y = int(y2)

                people.append({
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                    "confidence": confidence
                })

                centers.append([
                    center_x,
                    center_y
                ])

        # -----------------------------
        # CROWD CLUSTERING
        # -----------------------------

        clusters = []

        if len(centers) >= MIN_PEOPLE:

            points = np.array(centers)

            clustering = DBSCAN(
                eps=DBSCAN_EPS,
                min_samples=MIN_PEOPLE
            ).fit(points)

            labels = clustering.labels_

            for label in set(labels):

                if label == -1:
                    continue

                cluster_points = points[
                    labels == label
                ]

                if len(cluster_points) < MIN_PEOPLE:
                    continue

                clusters.append(cluster_points)

        # -----------------------------
        # CROWD ZONES
        # -----------------------------

        crowd_zones = []

        for index, cluster in enumerate(clusters):

            min_x = int(np.min(cluster[:, 0]))
            min_y = int(np.min(cluster[:, 1]))

            max_x = int(np.max(cluster[:, 0]))
            max_y = int(np.max(cluster[:, 1]))

            min_x = max(0, min_x - PADDING)
            min_y = max(0, min_y - PADDING)

            max_x = min(
                frame.shape[1] - 1,
                max_x + PADDING
            )

            max_y = min(
                frame.shape[0] - 1,
                max_y + PADDING
            )

            # -----------------------------
            # DENSITY
            # -----------------------------

            zone_area = max(
                1,
                (max_x - min_x) *
                (max_y - min_y)
            )

            density = (
                len(cluster) /
                zone_area *
                100000
            )

            # -----------------------------
            # RISK
            # -----------------------------

            if density < 5:
                risk = "LOW"

            elif density < 12:
                risk = "MEDIUM"

            else:
                risk = "HIGH"

            crowd_zones.append({
                "zone_id": index + 1,

                "x1": min_x,
                "y1": min_y,
                "x2": max_x,
                "y2": max_y,

                "people": len(cluster),

                "density": round(
                    float(density),
                    2
                ),

                "risk": risk
            })

        # -----------------------------
        # FINAL RESULT
        # -----------------------------

        return {
            "total_people": len(people),
            "crowd_zones": crowd_zones,
            "people": people
        }