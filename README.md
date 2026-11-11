# Camera-Based Sign-to-Speech Prototype

Prototype of the capstone "IoT-Based Smart Glove for Speech-Impaired Individuals of Tayug, Pangasinan",
using the device camera instead of the glove hardware.

| Glove design | This prototype |
|---|---|
| 5 flex sensors | Finger bend values (0-100%) computed from 21 hand landmarks (MediaPipe) |
| IMU | Hand tilt angle and hand size |
| Machine-learning model | scikit-learn RandomForest trained on your own samples (rule-based fallback included) |
| Text-to-speech engine | pyttsx3 (offline) |
| Python + Visual Studio Code | Python 3.9 - 3.12, runs in VS Code or Antigravity |

## Setup (VS Code / Antigravity)

1. Install **Python 3.10, 3.11 or 3.12** (MediaPipe 0.10.14 does not support 3.13 yet).
2. Open this folder (`smart_glove_camera`) in VS Code or Antigravity.
3. Open the terminal and create the environment:

   Windows:
   ```
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   macOS / Linux:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Select the `.venv` interpreter (Ctrl+Shift+P, "Python: Select Interpreter").
   On Windows, change `python.defaultInterpreterPath` in `.vscode/settings.json` to `${workspaceFolder}/.venv/Scripts/python.exe`.

## Run

### Option 1: Desktop App (OpenCV)
```
python src/run_app.py
```
Hold a gesture for about 0.8 seconds to add the word and hear it.
Keys: `h` toggle gesture manual, `s` speak sentence, `c` clear, `Backspace` undo, `a` auto-speak on/off, `m` model/rules, `q` quit.

### Option 2: Web Edition (Browser)
You can also run it directly inside your web browser (Chrome, Edge, Safari):
```
python src/run_web.py
```
Or simply double-click [`web/index.html`](web/index.html) to open it in your browser!
It uses HTML5 webcam access, MediaPipe JavaScript, and the browser's speech synthesis engine (`window.speechSynthesis`).

## Gesture & Sign Manual

> See [GESTURE_MANUAL.md](GESTURE_MANUAL.md) for full descriptions, tips, and embedded hand drawing diagrams ([`hand_drawings_manual.jpg`](hand_drawings_manual.jpg) and [`hand_sketch_guide.png`](hand_sketch_guide.png)).

You can use **either hand** (Right or Left). The 5 fingers are checked in order: (Thumb, Index, Middle, Ring, Pinky), where **1 = Extended** and **0 = Curled**:

| Word | Pattern | How to Pose Your Hand |
|---|:---:|---|
| **HELLO** | `(1, 1, 1, 1, 1)` | Open palm (all 5 fingers out) |
| **THANK YOU** | `(0, 1, 1, 1, 1)` | 4 fingers flat, thumb tucked against palm |
| **YES** | `(0, 0, 0, 0, 0)` | Closed fist (all fingers curled) |
| **NO** | `(1, 1, 1, 0, 0)` | Thumb + Index + Middle out, Ring & Pinky in |
| **GOOD** | `(1, 0, 0, 0, 0)` | Thumbs Up (thumb pointed straight up) |
| **YOU** | `(0, 1, 0, 0, 0)` | Point Index finger straight up |
| **PEACE** | `(0, 1, 1, 0, 0)` | Index + Middle extended (Peace / "V" sign) |
| **WATER** | `(0, 1, 1, 1, 0)` | Index + Middle + Ring extended ("W" sign) |
| **CALL ME** | `(1, 0, 0, 0, 1)` | Thumb + Pinky extended (Shaka / Phone sign) |
| **I LOVE YOU** | `(1, 1, 0, 0, 1)` | Thumb + Index + Pinky extended (ASL ILY sign) |

## Train your own model (recommended for the paper)

1. `python src/collect_data.py` - press `1`-`9`/`0` to pick a gesture, `SPACE` to record, move the hand slightly
   and record about 300 samples per gesture. Press `q` when finished.
2. `python src/train_model.py` - prints accuracy, a classification report, and a confusion matrix
   (useful for your testing chapter) and saves `models/gesture_model.joblib`.
3. `python src/run_app.py` - now uses the trained model automatically.

## Change the gestures

Edit `GESTURES` (name -> spoken text) and `RULES` in `src/config.py`.

## Folder structure

```
smart_glove_camera/
  src/config.py          settings and gesture list
  src/hand_features.py   camera -> landmarks -> finger values
  src/collect_data.py    record samples
  src/train_model.py     train and evaluate the classifier
  src/run_app.py         live recognition + speech
  src/tts.py             text-to-speech
  data/                  recorded samples (gestures.csv)
  models/                trained model
```

## Limitations

- Recognizes static single-hand gestures only (no motion or two-hand signs).
- Needs good lighting and the hand fully in view.
- The sample gestures are examples; replace them with your selected ASL gestures.
