"""Live sign-to-speech app.

Keys: s = speak sentence   c = clear   BACKSPACE = undo last word
      a = auto-speak on/off   m = switch trained model / rules
      h = toggle on-screen gesture manual   q = quit
"""
import sys
import time
from pathlib import Path

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cv2
import joblib
from config import (CAMERA_INDEX, GESTURES, HOLD_SECONDS, MIN_CONFIDENCE, MODEL_PATH)
from hand_features import (FINGER_NAMES, HandTracker, analyse, rule_classify,
                           to_feature_vector, to_points)
from tts import Speaker

# Quick visual guide for each sign (works with either Left or Right hand)
GESTURE_TIPS = [
    ("HELLO", "Open palm (all 5 fingers out)"),
    ("THANK YOU", "4 fingers out, thumb tucked in"),
    ("YES", "Closed fist (all fingers curled)"),
    ("NO", "Thumb + Index + Middle out"),
    ("GOOD", "Thumbs Up (thumb up, fist closed)"),
    ("YOU", "Index pointing up"),
    ("PEACE", "Index + Middle (V / Peace sign)"),
    ("WATER", "Index + Middle + Ring (W sign)"),
    ("CALL ME", "Thumb + Pinky out (Shaka / Phone)"),
    ("I LOVE YOU", "Thumb + Index + Pinky out (ILY)"),
]


def put(frame, text, org, scale=0.6, color=(255, 255, 255), thick=2):
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def draw_manual_overlay(frame, current_gesture, w, h, toggle_rect):
    """Draw a semi-transparent on-screen cheat sheet of all available hand signs."""
    panel_w = min(350, int(w * 0.52))
    panel_h = min(h - 130, 320)
    x1, y1 = max(10, w - panel_w - 10), 70
    x2, y2 = w - 10, y1 + panel_h

    # Translucent card background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 100), 1)

    # Header & Close button
    put(frame, "GESTURE MANUAL", (x1 + 10, y1 + 22), 0.48, (0, 255, 140), 1)
    
    # Close button in top-right of panel: [X Close]
    close_w, close_h = 100, 22
    cx1, cy1 = x2 - close_w - 6, y1 + 6
    cx2, cy2 = x2 - 6, y1 + 6 + close_h
    toggle_rect[0], toggle_rect[1], toggle_rect[2], toggle_rect[3] = cx1, cy1, cx2, cy2
    cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (60, 30, 30), -1)
    cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (100, 120, 255), 1)
    put(frame, "Close [H]", (cx1 + 12, cy1 + 15), 0.38, (220, 220, 255), 1)

    for idx, (name, tip) in enumerate(GESTURE_TIPS):
        line_y = y1 + 45 + idx * 26
        if line_y + 16 > y2:
            break
        is_active = (current_gesture == name)
        name_color = (0, 255, 255) if is_active else (240, 240, 240)
        marker = "> " if is_active else "  "
        put(frame, f"{marker}{name}: {tip}", (x1 + 6, line_y), 0.35, name_color, 1)


def draw_open_button(frame, w, toggle_rect):
    """Draw the clickable [H: Open Manual] pill at top-right when manual is closed."""
    btn_w, btn_h = 160, 32
    bx1, by1 = w - btn_w - 12, 12
    bx2, by2 = w - 12, 12 + btn_h
    toggle_rect[0], toggle_rect[1], toggle_rect[2], toggle_rect[3] = bx1, by1, bx2, by2
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (35, 45, 40), -1)
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 220, 110), 2)
    put(frame, "[H] Open Manual", (bx1 + 10, by1 + 21), 0.45, (0, 255, 150), 1)


def main():
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    use_model = model is not None
    print("Using trained model" if use_model else "No trained model found - using rule-based mode")

    tracker, speaker = HandTracker(), Speaker()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"\n[ERROR] Could not open camera (index {CAMERA_INDEX}).")
        print("Please check that your webcam is connected and not currently used by another program.")
        print("If you have multiple webcams, try setting CAMERA_INDEX = 1 in src/config.py.\n")
        tracker.close()
        speaker.close()
        return

    words, cand, since, committed, auto = [], None, 0.0, None, True
    show_manual = False  # Start closed so the camera is clear; press H or click to open
    toggle_rect = [0, 0, 0, 0]  # Clickable area for open/close button

    win_name = "Sign-to-Speech (camera prototype)"
    cv2.namedWindow(win_name)

    def on_mouse(event, x, y, flags, param):
        nonlocal show_manual
        if event == cv2.EVENT_LBUTTONDOWN:
            if toggle_rect[0] <= x <= toggle_rect[2] and toggle_rect[1] <= y <= toggle_rect[3]:
                show_manual = not show_manual

    cv2.setMouseCallback(win_name, on_mouse)

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        lm, hand = tracker.process(frame)
        gesture, conf = None, 0.0

        if lm is not None:
            tracker.draw(frame, lm)
            pts = to_points(lm, w, h)
            a = analyse(pts)
            if use_model:
                x = to_feature_vector(pts, a["bend"], hand).reshape(1, -1)
                proba = model.predict_proba(x)[0]
                best = int(proba.argmax())
                if proba[best] >= MIN_CONFIDENCE:
                    gesture, conf = model.classes_[best], float(proba[best])
            else:
                gesture = rule_classify(a)
            # finger "sensor" bars
            for i, b in enumerate(a["bend"]):
                y = 110 + i * 24
                put(frame, FINGER_NAMES[i], (10, y + 12), 0.45)
                cv2.rectangle(frame, (80, y), (180, y + 14), (70, 70, 70), -1)
                cv2.rectangle(frame, (80, y), (80 + int(100 * b), y + 14), (255, 160, 0), -1)
            put(frame, f"Tilt: {a['tilt']:.0f} deg   Hand: {'Right' if hand == 'Left' else 'Left'}",
                (10, 250), 0.5)
            if a["palm"] < 40:
                put(frame, "Move hand closer", (10, 275), 0.5, (0, 200, 255))

        # hold-to-confirm logic
        now = time.time()
        if gesture != cand:
            cand, since = gesture, now
            if gesture is None:
                committed = None
        progress = 0.0
        if gesture is not None:
            progress = 1.0 if gesture == committed else min((now - since) / HOLD_SECONDS, 1.0)
            if gesture != committed and now - since >= HOLD_SECONDS:
                committed = gesture
                words.append(gesture)
                if auto:
                    speaker.say(GESTURES.get(gesture, gesture.title()))

        # overlay
        cv2.rectangle(frame, (0, 0), (w, 60), (30, 30, 30), -1)
        put(frame, gesture if gesture else "-", (10, 38), 1.0, (0, 255, 120), 2)
        if conf:
            put(frame, f"{conf * 100:.0f}%", (w - 70, 38), 0.7)
        cv2.rectangle(frame, (0, 60), (int(w * progress), 68), (0, 220, 100), -1)
        cv2.rectangle(frame, (0, h - 50), (w, h), (30, 30, 30), -1)
        sentence = " ".join(GESTURES.get(g, g.title()) for g in words)
        put(frame, sentence[-60:], (10, h - 18), 0.8)
        put(frame, f"[{'MODEL' if use_model else 'RULES'}]  h:manual({'open' if show_manual else 'closed'})  s:speak  c:clear  a:auto({'on' if auto else 'off'})  q:quit",
            (10, h - 56), 0.42, (200, 200, 200), 1)

        # Draw either the Open button or the full Manual card
        if show_manual:
            draw_manual_overlay(frame, gesture, w, h, toggle_rect)
        else:
            draw_open_button(frame, w, toggle_rect)

        cv2.imshow(win_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key in (ord("h"), ord("H"), ord("?")):
            show_manual = not show_manual
        elif key == ord("s"):
            speaker.say(sentence)
        elif key == ord("c"):
            words.clear()
        elif key == 8 and words:
            words.pop()
        elif key == ord("a"):
            auto = not auto
        elif key == ord("m") and model is not None:
            use_model = not use_model

    tracker.close()
    speaker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
