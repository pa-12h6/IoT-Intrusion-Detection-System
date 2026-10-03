from pathlib import Path
from time import perf_counter

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.tree import DecisionTreeClassifier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "ids_multiclass.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "model_comparison.csv"

data = pd.read_csv(DATA_FILE)

train_data = data[data["Split"] == "train"]
test_data = data[data["Split"] == "test"]

metadata_columns = ["Label", "SourceFile", "Split"]
X_train = train_data.drop(columns=metadata_columns)
y_train = train_data["Label"]
X_test = test_data.drop(columns=metadata_columns)
y_test = test_data["Label"]

models = {
    "Majority baseline": DummyClassifier(strategy="most_frequent"),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    ),
    "Extra Trees": ExtraTreesClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    ),
}

results = []
trained_models = {}

for name, model in models.items():
    print(f"Training {name}...")
    start_time = perf_counter()
    model.fit(X_train, y_train)
    training_seconds = perf_counter() - start_time

    start_time = perf_counter()
    predictions = model.predict(X_test)
    prediction_seconds = perf_counter() - start_time

    results.append(
        {
            "Model": name,
            "Accuracy": accuracy_score(y_test, predictions),
            "Macro F1": f1_score(y_test, predictions, average="macro"),
            "Weighted F1": f1_score(y_test, predictions, average="weighted"),
            "Training seconds": training_seconds,
            "Prediction seconds": prediction_seconds,
        }
    )
    trained_models[name] = (model, predictions)

comparison = pd.DataFrame(results).sort_values(
    by=["Macro F1", "Accuracy"],
    ascending=False,
)

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
comparison.to_csv(REPORT_FILE, index=False)

print("\nModel comparison:")
print(comparison.to_string(index=False, formatters={
    "Accuracy": "{:.4f}".format,
    "Macro F1": "{:.4f}".format,
    "Weighted F1": "{:.4f}".format,
    "Training seconds": "{:.2f}".format,
    "Prediction seconds": "{:.2f}".format,
}))

best_name = comparison.iloc[0]["Model"]
best_model, best_predictions = trained_models[best_name]

print(f"\nBest model by Macro F1: {best_name}")
print("\nDetailed classification report for the best model:")
print(classification_report(y_test, best_predictions, zero_division=0))

print(f"\nSaved comparison table to: {REPORT_FILE}")