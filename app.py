from datetime import datetime
from pathlib import Path
import sqlite3

import joblib
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_FILE = PROJECT_ROOT / "models" / "ids_random_forest_multiclass.joblib"
DATABASE_FILE = PROJECT_ROOT / "data" / "processed" / "ids_history.db"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB upload limit

model = joblib.load(MODEL_FILE)
feature_columns = list(model.feature_names_in_)


def initialize_database():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analyzed_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                analyzed_rows INTEGER NOT NULL,
                invalid_rows INTEGER NOT NULL,
                attack_rows INTEGER NOT NULL,
                attack_percentage REAL NOT NULL,
                class_summary TEXT NOT NULL
            )
            """
        )


def save_upload_history(
    filename,
    total_rows,
    analyzed_rows,
    invalid_rows,
    attack_rows,
    attack_percentage,
    class_summary,
):
    analyzed_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO upload_history (
                analyzed_at,
                filename,
                total_rows,
                analyzed_rows,
                invalid_rows,
                attack_rows,
                attack_percentage,
                class_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analyzed_at,
                filename,
                total_rows,
                analyzed_rows,
                invalid_rows,
                attack_rows,
                attack_percentage,
                class_summary,
            ),
        )


initialize_database()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    uploaded_file = request.files.get("traffic_file")

    if uploaded_file is None or uploaded_file.filename == "":
        return render_template("index.html", error="Choose a CSV file first.")

    try:
        traffic = pd.read_csv(uploaded_file)
    except Exception as error:
        return render_template(
            "index.html",
            error=f"Could not read that file as CSV: {error}",
        )

    missing_columns = [
        column for column in feature_columns
        if column not in traffic.columns
    ]
    if missing_columns:
        return render_template(
            "index.html",
            error="This CSV is missing required feature columns: "
            + ", ".join(missing_columns),
        )

    features = traffic[feature_columns].apply(pd.to_numeric, errors="coerce")
    features = features.replace(
        [float("inf"), float("-inf")],
        float("nan"),
    )

    valid_rows = features.notna().all(axis=1)
    invalid_count = int((~valid_rows).sum())
    features = features.loc[valid_rows]

    if features.empty:
        return render_template(
            "index.html",
            error="No rows had complete numeric values for all required features.",
        )

    predictions = model.predict(features)

    prediction_counts = (
        pd.Series(predictions)
        .value_counts()
        .rename_axis("class_name")
        .reset_index(name="count")
    )
    prediction_counts_list = [
        {
            "class_name": str(row["class_name"]),
            "count": int(row["count"]),
        }
        for _, row in prediction_counts.iterrows()
    ]

    attack_rows = int((predictions != "Benign").sum())
    attack_percentage = attack_rows / len(predictions) * 100

    class_summary = ", ".join(
        f"{item['class_name']}: {item['count']}"
        for item in prediction_counts_list
    )

    safe_filename = secure_filename(uploaded_file.filename) or "uploaded.csv"
    save_upload_history(
        filename=safe_filename,
        total_rows=len(traffic),
        analyzed_rows=len(features),
        invalid_rows=invalid_count,
        attack_rows=attack_rows,
        attack_percentage=attack_percentage,
        class_summary=class_summary,
    )

    preview = features.head(20).copy()
    preview.insert(0, "Prediction", predictions[: len(preview)])
    preview = preview.to_dict(orient="records")

    return render_template(
        "results.html",
        total_rows=len(traffic),
        analyzed_rows=len(features),
        invalid_rows=invalid_count,
        prediction_counts=prediction_counts_list,
        preview=preview,
        attack_rows=attack_rows,
        attack_percentage=attack_percentage,
    )


@app.route("/history")
def history():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.row_factory = sqlite3.Row
        records = connection.execute(
            """
            SELECT *
            FROM upload_history
            ORDER BY id DESC
            LIMIT 100
            """
        ).fetchall()

    return render_template("history.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)