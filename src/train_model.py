from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "ids_multiclass.csv"
MODEL_FILE = PROJECT_ROOT / "models" / "ids_random_forest_multiclass.joblib"

data = pd.read_csv(DATA_FILE)

train_data = data[data["Split"] == "train"]
test_data = data[data["Split"] == "test"]

metadata_columns = ["Label", "SourceFile", "Split"]
X_train = train_data.drop(columns=metadata_columns)
y_train = train_data["Label"]
X_test = test_data.drop(columns=metadata_columns)
y_test = test_data["Label"]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("Test files by class:")
print(test_data.groupby("Label")["SourceFile"].unique().to_string())

print(f"\nTraining rows: {len(X_train):,}")
print(f"Test rows: {len(X_test):,}")
print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

print("Confusion matrix (rows = actual, columns = predicted):")
print(confusion_matrix(y_test, predictions, labels=model.classes_))
print("Class order:", list(model.classes_))

MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_FILE)
print(f"\nSaved model to: {MODEL_FILE}")