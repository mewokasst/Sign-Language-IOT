"""Camera -> hand landmarks -> finger values (the software version of the flex sensors + IMU)."""
import math
import sys
from pathlib import Path

# Ensure src directory is in sys.path for direct or module imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cv2
import numpy as np
import mediapipe as mp
from config import RULES

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]


class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False, max_num_hands=1, model_complexity=1,
            min_detection_confidence=0.6, min_tracking_confidence=0.5)

    def process(self, frame_bgr):
        """Return (landmark_list, handedness_label) or (None, None)."""
        res = self.hands.process(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        if not res.multi_hand_landmarks or not res.multi_handedness:
            return None, None
        handedness = "Right"
        if res.multi_handedness and res.multi_handedness[0].classification:
            handedness = res.multi_handedness[0].classification[0].label
        return res.multi_hand_landmarks[0], handedness

    def draw(self, frame, landmarks):
        mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    def close(self):
        self.hands.close()


def to_points(landmarks, w, h):
    """21 landmarks -> array of pixel coordinates (x, y, z)."""
    return np.array([[p.x * w, p.y * h, p.z * w] for p in landmarks.landmark], dtype=np.float32)


def _d(a, b):
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


def analyse(pts):
    """Finger bend (0 = straight, 1 = fully bent), extended flags, tilt and palm size."""
    wrist = pts[0]
    palm = _d(pts[5], pts[17]) + 1e-6
    bend = [0.0] * 5
    ext = [0] * 5
    t = _d(pts[4], pts[17]) / palm                      # thumb: tip distance from pinky base
    ext[0] = int(t > 1.3)
    bend[0] = float(np.clip((1.8 - t) / 1.1, 0, 1))
    for i, (mcp, tip) in enumerate([(5, 8), (9, 12), (13, 16), (17, 20)], start=1):
        r = _d(pts[tip], wrist) / (_d(pts[mcp], wrist) + 1e-6)   # tip vs knuckle distance from wrist
        ext[i] = int(r > 1.5)
        bend[i] = float(np.clip((1.9 - r) / 0.9, 0, 1))
    thumb_up = (pts[2][1] - pts[4][1]) > 0.8 * palm      # image y grows downward
    tilt = math.degrees(math.atan2(pts[9][0] - wrist[0], wrist[1] - pts[9][1]))
    return {"ext": tuple(ext), "bend": bend, "thumb_up": bool(thumb_up), "tilt": tilt, "palm": palm}


def to_feature_vector(pts, bend, handedness):
    """Position/size independent features for the ML model (63 coordinates + 5 bends)."""
    p = pts - pts[0]                                     # wrist at origin
    p = p / (_d(pts[5], pts[17]) + 1e-6)                 # palm width = 1
    if handedness == "Left":                             # make both hands look the same
        p[:, 0] = -p[:, 0]
    return np.concatenate([p.flatten(), np.array(bend, dtype=np.float32)])


def rule_classify(a):
    for name, pattern in RULES.items():
        if a["ext"] == pattern and (name != "GOOD" or a["thumb_up"]):
            return name
    return None
