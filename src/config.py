"""Settings shared by every script. Edit GESTURES to change the signs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "gestures.csv"
MODEL_PATH = ROOT / "models" / "gesture_model.joblib"

CAMERA_INDEX = 0          # try 1 if you have an external webcam
HOLD_SECONDS = 0.8        # how long a gesture must be held before it is added
MIN_CONFIDENCE = 0.70     # minimum model confidence (trained model only)

# Gesture name -> text that is spoken.
# Finger order for RULES: thumb, index, middle, ring, pinky (1 = extended, 0 = curled)
GESTURES = {
    "HELLO":      "Hello",
    "THANK YOU":  "Thank you",
    "YES":        "Yes",
    "NO":         "No",
    "GOOD":       "Good",
    "YOU":        "You",
    "PEACE":      "Peace",
    "WATER":      "Water",
    "CALL ME":    "Call me",
    "I LOVE YOU": "I love you",
}
GESTURE_NAMES = list(GESTURES.keys())

# Rule-based fallback used until you train your own model.
RULES = {
    "HELLO":      (1, 1, 1, 1, 1),
    "THANK YOU":  (0, 1, 1, 1, 1),
    "YES":        (0, 0, 0, 0, 0),
    "NO":         (1, 1, 1, 0, 0),
    "GOOD":       (1, 0, 0, 0, 0),   # also needs the thumb to point up
    "YOU":        (0, 1, 0, 0, 0),
    "PEACE":      (0, 1, 1, 0, 0),
    "WATER":      (0, 1, 1, 1, 0),
    "CALL ME":    (1, 0, 0, 0, 1),
    "I LOVE YOU": (1, 1, 0, 0, 1),
}
