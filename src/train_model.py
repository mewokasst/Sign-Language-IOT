"""Train the gesture classifier from data/gestures.csv and save it to models/."""
import sys
from pathlib import Path

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from config import DATA_PATH, MODEL_PATH


def main():
    if not DATA_PATH.exists() or DATA_PATH.stat().st_size == 0:
        raise SystemExit("No data yet (data/gestures.csv is missing or empty). Run collect_data.py first.")
    df = pd.read_csv(DATA_PATH, header=None)
    y = df[0]
    X = df.drop(columns=[0]).values
    print(f"{len(df)} samples, {y.nunique()} gestures")
    print(y.value_counts().to_string(), "\n")
    if y.nunique() < 2:
        raise SystemExit("Record at least 2 different gestures to train the model.")

    # Check if all classes have enough samples for stratified split
    min_samples = y.value_counts().min()
    stratify = y if min_samples >= 2 else None
    if min_samples < 2:
        print("[Notice] Some gestures have only 1 sample, training without stratification.\n")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=stratify, random_state=42)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    print("Test accuracy:", round((pred == y_te).mean() * 100, 2), "%\n")
    print(classification_report(y_te, pred, zero_division=0))
    print("Confusion matrix (rows = actual):")
    print(confusion_matrix(y_te, pred, labels=model.classes_))

    model.fit(X, y)  # final model uses all samples
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("\nModel saved to", MODEL_PATH)


if __name__ == "__main__":
    main()
