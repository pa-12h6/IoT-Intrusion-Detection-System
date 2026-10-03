from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "ids_multiclass.csv"
MODEL_FILE = PROJECT_ROOT / "models" / "ids_random_forest_multiclass.joblib"
REPORTS_DIR = PROJECT_ROOT / "reports"

CONFUSION_MATRIX_FILE = REPORTS_DIR / "confusion_matrix.png"
FEATURE_IMPORTANCE_FILE = REPORTS_DIR / "feature_importance.png"

sns.set_theme(style="whitegrid")

data = pd.read_csv(DATA_FILE)
test_data = data[data["Split"] == "test"]

metadata_columns = ["Label", "SourceFile", "Split"]
X_test = test_data.drop(columns=metadata_columns)
y_test = test_data["Label"]

model = joblib.load(MODEL_FILE)
predictions = model.predict(X_test)
class_names = model.classes_

# Save the confusion matrix.
matrix = confusion_matrix(y_test, predictions, labels=class_names)

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
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CONFUSION_MATRIX_FILE, dpi=160)
plt.close()

# Save a chart of the 15 most important model features.
importance = pd.Series(
    model.feature_importances_,
    index=model.feature_names_in_,
).nlargest(15).sort_values()

plt.figure(figsize=(10, 7))
sns.barplot(
    x=importance.values,
    y=importance.index,
    color="#1769aa",
)
plt.title("Top 15 Feature Importances")
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig(FEATURE_IMPORTANCE_FILE, dpi=160)
plt.close()

print(f"Saved confusion matrix to: {CONFUSION_MATRIX_FILE}")
print(f"Saved feature importance chart to: {FEATURE_IMPORTANCE_FILE}")