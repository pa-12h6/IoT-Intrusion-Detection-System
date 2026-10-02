from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "ids_multiclass.csv"
MODEL_FILE = PROJECT_ROOT / "models" / "ids_random_forest_multiclass.joblib"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "confusion_matrix.png"

data = pd.read_csv(DATA_FILE)
test_data = data[data["Split"] == "test"]

metadata_columns = ["Label", "SourceFile", "Split"]
X_test = test_data.drop(columns=metadata_columns)
y_test = test_data["Label"]

model = joblib.load(MODEL_FILE)
predictions = model.predict(X_test)
class_names = model.classes_

matrix = confusion_matrix(y_test, predictions, labels=class_names)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(9, 7))
sns.heatmap(
    matrix,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_names,
    yticklabels=class_names,
)
plt.title("IoT Intrusion Detection: Confusion Matrix")
plt.xlabel("Predicted class")
plt.ylabel("Actual class")
plt.xticks(rotation=30, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=160)
plt.close()

print(f"Saved confusion matrix to: {OUTPUT_FILE}")