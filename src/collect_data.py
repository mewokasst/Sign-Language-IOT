"""Record your own samples for each gesture.

Keys:  1-9, 0 = choose gesture (0 is the 10th)   SPACE = start/stop recording
       q = quit
"""
import csv
import sys
from pathlib import Path

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cv2
from config import CAMERA_INDEX, DATA_PATH, GESTURE_NAMES
from hand_features import HandTracker, analyse, to_feature_vector, to_points

KEYS = {ord(str((i + 1) % 10)): i for i in range(min(10, len(GESTURE_NAMES)))}


def load_counts():
    counts = {g: 0 for g in GESTURE_NAMES}
    if DATA_PATH.exists():
        with open(DATA_PATH, newline="") as f:
            for row in csv.reader(f):
                if row and row[0] in counts:
                    counts[row[0]] += 1
    return counts


def main():
    DATA_PATH.parent.mkdir(exist_ok=True)
    new_file = not DATA_PATH.exists()

    counts, current, recording = load_counts(), 0, False
    tracker, cap = HandTracker(), cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"\n[ERROR] Could not open camera (index {CAMERA_INDEX}).")
        print("Please check that your webcam is connected and not currently used by another program.")
        print("If you have multiple webcams, try setting CAMERA_INDEX = 1 in src/config.py.\n")
        tracker.close()
        return

    out = open(DATA_PATH, "a", newline="")
    writer = csv.writer(out)
    if new_file:
        pass  # no header: first column is the label, the rest are features

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        lm, hand = tracker.process(frame)
        if lm is not None:
            tracker.draw(frame, lm)
            pts = to_points(lm, w, h)
            a = analyse(pts)
            if recording:
                name = GESTURE_NAMES[current]
                writer.writerow([name, *to_feature_vector(pts, a["bend"], hand).tolist()])
                counts[name] += 1

        name = GESTURE_NAMES[current]
        color = (0, 0, 255) if recording else (0, 200, 0)
        cv2.rectangle(frame, (0, 0), (w, 70), (30, 30, 30), -1)
        cv2.putText(frame, f"Gesture: {name}  ({counts[name]} samples)", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, "REC" if recording else "Press SPACE to record", (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        for i, g in enumerate(GESTURE_NAMES):
            cv2.putText(frame, f"{(i + 1) % 10}: {g} ({counts[g]})", (10, 100 + i * 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255) if i == current else (160, 160, 160), 1)
        cv2.imshow("Collect gesture data", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            recording = not recording
        if key in KEYS:
            current, recording = KEYS[key], False

    out.close()
    tracker.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Saved to", DATA_PATH)


if __name__ == "__main__":
    main()
