"""Main unified launcher for the Smart Glove Sign-to-Speech Prototype.

Run with:
    python main.py
Or choose directly:
    python main.py --web
    python main.py --desktop
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


def run_web():
    print("\n[Launching Web Edition in your default browser...]")
    web_script = ROOT / "src" / "run_web.py"
    subprocess.run([PYTHON, str(web_script)])


def run_desktop():
    print("\n[Launching Desktop Camera App (OpenCV)...]")
    desktop_script = ROOT / "src" / "run_app.py"
    subprocess.run([PYTHON, str(desktop_script)])


def run_collect():
    print("\n[Launching Gesture Data Collection...]")
    collect_script = ROOT / "src" / "collect_data.py"
    subprocess.run([PYTHON, str(collect_script)])


def run_train():
    print("\n[Training Gesture Classifier Model...]")
    train_script = ROOT / "src" / "train_model.py"
    subprocess.run([PYTHON, str(train_script)])


def menu():
    print("\n" + "=" * 64)
    print("        🖐️ SMART GLOVE SIGN-TO-SPEECH PROTOTYPE")
    print("=" * 64)
    print("  [1] Run Web Edition (Opens in your Web Browser) [RECOMMENDED]")
    print("  [2] Run Desktop Window (Python OpenCV Camera App)")
    print("  [3] Record Gesture Training Samples (collect_data.py)")
    print("  [4] Train Model (train_model.py)")
    print("  [5] Exit")
    print("=" * 64)
    
    try:
        choice = input("Enter your choice (1-5, default is 1): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        return

    if choice in ("1", "", "web"):
        run_web()
    elif choice in ("2", "desktop"):
        run_desktop()
    elif choice == "3":
        run_collect()
    elif choice == "4":
        run_train()
    elif choice == "5":
        print("Goodbye!")
    else:
        print(f"Unknown choice '{choice}'. Running Web Edition by default...")
        run_web()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip("-")
        if arg in ("web", "w", "browser"):
            run_web()
        elif arg in ("desktop", "d", "app"):
            run_desktop()
        elif arg in ("collect", "c"):
            run_collect()
        elif arg in ("train", "t"):
            run_train()
        else:
            print(f"Usage: python main.py [--web | --desktop | --collect | --train]")
    else:
        menu()

