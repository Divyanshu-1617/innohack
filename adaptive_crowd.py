import cv2
import math
from ultralytics import YOLO

# ============================================================
# ADAPTIVE CROWD GROUPING - STEP 2
#
# This version:
#   1. Detects people with the trained YOLO model
#   2. Uses the bottom-center (foot position) of each bbox
#   3. Uses an adaptive distance threshold based on person size
#   4. Builds groups using connected components / union-find
#   5. Displays groups, but does NOT classify High/Medium/Low yet
#
# IMPORTANT:
#   This is a new prototype. It does not modify zone_density.py.
# ============================================================


# ============================================================
# MODEL
# ============================================================

MODEL_PATH = r"D:\innohack\models\mot20_person_v1_best.pt"

model = YOLO(MODEL_PATH)


# ============================================================
# CCTV SEQUENCE
# ============================================================

IMAGE_DIR = r"D:\innohack\datasets\mot20\train\MOT20-01\img1"

START_FRAME = 1
END_FRAME = 429


# ============================================================
# DETECTION SETTINGS
# ============================================================

CONFIDENCE = 0.15
IMAGE_SIZE = 960
DEVICE = 0


# ============================================================
# GROUPING SETTINGS
# ============================================================

# A group containing fewer than this number of people will still
# be displayed, but will NOT be considered a crowd.
MIN_CROWD_PEOPLE = 5

# Person-height multiplier used to calculate adaptive distance.
#
# Example:
#   average person height = 150 px
#   threshold = 150 * 0.75 = 112.5 px
#
# Increase this if groups are being split too aggressively.
# Decrease it if unrelated people are being merged.
DISTANCE_SCALE = 0.75

# Safety limits for the adaptive threshold.
MIN_DISTANCE = 45
MAX_DISTANCE = 150


# ============================================================
# UNION-FIND / DISJOINT SET
# ============================================================

class UnionFind:

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):

        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b

        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a

        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1


# ============================================================
# ADAPTIVE DISTANCE
# ============================================================

def adaptive_distance(person_a, person_b):
    """
    Calculate the maximum allowed distance between two people.

    Each person contains:
        x       = foot x
        y       = foot y
        height  = bounding-box height

    We use the average apparent person height as a rough
    perspective-aware scale.

    Smaller people (farther away) -> smaller threshold.
    Larger people (closer to camera) -> larger threshold.
    """

    height_a = person_a["height"]
    height_b = person_b["height"]

    average_height = (height_a + height_b) / 2.0

    threshold = average_height * DISTANCE_SCALE

    threshold = max(MIN_DISTANCE, threshold)
    threshold = min(MAX_DISTANCE, threshold)

    return threshold


# ============================================================
# EUCLIDEAN DISTANCE
# ============================================================

def euclidean_distance(person_a, person_b):

    dx = person_a["foot_x"] - person_b["foot_x"]
    dy = person_a["foot_y"] - person_b["foot_y"]

    return math.sqrt(dx * dx + dy * dy)


# ============================================================
# BUILD ADAPTIVE GROUPS
# ============================================================

def build_groups(people):
    """
    Connect nearby people using adaptive distances.

    If:
        distance(A, B) <= adaptive threshold

    then A and B belong to the same connected group.

    Connected components allow a chain such as:

        A -- B -- C

    to become one group even if A and C are not directly
    close enough to each other.
    """

    number_of_people = len(people)

    if number_of_people == 0:
        return []

    uf = UnionFind(number_of_people)

    # --------------------------------------------------------
    # Compare every pair of detected people
    # --------------------------------------------------------

    for i in range(number_of_people):

        for j in range(i + 1, number_of_people):

            distance = euclidean_distance(
                people[i],
                people[j]
            )

            threshold = adaptive_distance(
                people[i],
                people[j]
            )

            if distance <= threshold:
                uf.union(i, j)

    # --------------------------------------------------------
    # Convert connected components into groups
    # --------------------------------------------------------

    groups = {}

    for index in range(number_of_people):

        root = uf.find(index)

        if root not in groups:
            groups[root] = []

        groups[root].append(index)

    # Return groups as lists of person indices
    return list(groups.values())


# ============================================================
# GROUP BOUNDING BOX
# ============================================================

def get_group_bbox(group, people):

    x1 = min(people[i]["x1"] for i in group)
    y1 = min(people[i]["y1"] for i in group)
    x2 = max(people[i]["x2"] for i in group)
    y2 = max(people[i]["y2"] for i in group)

    return x1, y1, x2, y2


# ============================================================
# DISPLAY GROUP COLOR
# ============================================================

def group_color(group_size):

    if group_size >= MIN_CROWD_PEOPLE:
        # Crowd group
        return (0, 0, 255)

    # Small group / not crowd
    return (0, 255, 255)


# ============================================================
# PROCESS FRAMES
# ============================================================

cv2.namedWindow(
    "Adaptive Crowd Grouping",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Adaptive Crowd Grouping",
    1280,
    720
)


for frame_number in range(START_FRAME, END_FRAME + 1):

    image_path = (
        rf"{IMAGE_DIR}\{frame_number:06d}.jpg"
    )

    frame = cv2.imread(image_path)

    if frame is None:
        print(
            f"WARNING: Could not read frame {frame_number}"
        )
        continue

    # ========================================================
    # YOLO DETECTION
    # ========================================================

    results = model.predict(
        frame,
        classes=[0],
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        device=DEVICE,
        verbose=False
    )

    result = results[0]

    people = []

    # ========================================================
    # EXTRACT PERSON INFORMATION
    # ========================================================

    if result.boxes is not None:

        for detection in result.boxes:

            x1, y1, x2, y2 = (
                detection.xyxy[0]
                .cpu()
                .numpy()
            )

            confidence = float(
                detection.conf[0].cpu().numpy()
            )

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            width = x2 - x1
            height = y2 - y1

            # ------------------------------------------------
            # FOOT POSITION
            #
            # Instead of bbox center, use the bottom-center.
            # This is a better approximation of where the
            # person stands on the ground plane.
            # ------------------------------------------------

            foot_x = int((x1 + x2) / 2)
            foot_y = y2

            people.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": width,
                "height": height,
                "foot_x": foot_x,
                "foot_y": foot_y,
                "confidence": confidence
            })

    # ========================================================
    # BUILD ADAPTIVE GROUPS
    # ========================================================

    groups = build_groups(people)

    # Sort largest groups first
    groups.sort(
        key=lambda group: len(group),
        reverse=True
    )

    # ========================================================
    # DRAW GROUPS
    # ========================================================

    crowd_groups = 0

    for group_number, group in enumerate(groups, start=1):

        group_size = len(group)

        gx1, gy1, gx2, gy2 = get_group_bbox(
            group,
            people
        )

        color = group_color(group_size)

        if group_size >= MIN_CROWD_PEOPLE:
            crowd_groups += 1
            label = (
                f"GROUP {group_number} | "
                f"{group_size} PEOPLE | CROWD"
            )
        else:
            label = (
                f"GROUP {group_number} | "
                f"{group_size} PEOPLE"
            )

        # ----------------------------------------------------
        # Draw group bounding box
        # ----------------------------------------------------

        cv2.rectangle(
            frame,
            (gx1, gy1),
            (gx2, gy2),
            color,
            3
        )

        # ----------------------------------------------------
        # Label
        # ----------------------------------------------------

        text_y = max(30, gy1 - 10)

        cv2.putText(
            frame,
            label,
            (gx1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            color,
            2,
            cv2.LINE_AA
        )

        # ----------------------------------------------------
        # Draw small foot-position markers
        #
        # These are intentionally small. They help us debug
        # the grouping algorithm without creating the giant
        # clutter of individual YOLO boxes.
        # ----------------------------------------------------

        for person_index in group:

            person = people[person_index]

            cv2.circle(
                frame,
                (
                    person["foot_x"],
                    person["foot_y"]
                ),
                4,
                color,
                -1
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    total_people = len(people)

    cv2.rectangle(
        frame,
        (10, 10),
        (430, 100),
        (30, 30, 30),
        -1
    )

    cv2.putText(
        frame,
        f"TOTAL PEOPLE: {total_people}",
        (25, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"GROUPS: {len(groups)}",
        (25, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"CROWD GROUPS (5+): {crowd_groups}",
        (25, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Adaptive Crowd Grouping",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    # Pause with SPACE
    elif key == 32:

        while True:

            pause_key = cv2.waitKey(0) & 0xFF

            if pause_key == 32:
                break

            if pause_key == ord("q"):
                cv2.destroyAllWindows()
                raise SystemExit


cv2.destroyAllWindows()