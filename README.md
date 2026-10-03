# IoT Intrusion Detection System

A data science project that classifies IoT network traffic features using a Random Forest model. It includes a data preparation pipeline, model evaluation charts, and a Flask dashboard for CSV uploads and prediction history.

## Supported classes

The current model predicts four classes:

- Benign
- DDoS-UDP_Flood
- DoS-UDP_Flood
- Mirai-udpplain

## Evaluation

The model was evaluated on sampled rows from separate CICIoT2023 files that were not used for training. It achieved about **97.2% accuracy** across 11,998 test rows.

The largest confusion was between DDoS-UDP_Flood and DoS-UDP_Flood. The results apply to these classes and files from CICIoT2023; performance on other networks or datasets may differ.

### Confusion matrix

![Confusion matrix for the four traffic classes](reports/confusion_matrix.png)


### Most important model features

![Top 15 Random Forest feature importances](reports/feature_importance.png)

Feature importance shows which inputs the trained Random Forest used most when making predictions. It does not establish that a feature causes an attack.

## Dataset

This project uses CSV feature files from the [CICIoT2023 dataset](https://www.unb.ca/cic/datasets/iotdataset-2023.html), provided by the Canadian Institute for Cybersecurity at the University of New Brunswick.

Place the extracted CSV category folders under:

```text
data/raw/CSV/
```

The current preparation script uses the Benign, DDoS-UDP_Flood, DoS-UDP_Flood, and Mirai-udpplain folders. It samples separate files for training and testing. Keep the original dataset files unchanged.

## Project structure

```text
IoT-Intrusion-Detection-System/
├── app.py
├── data/
│   ├── raw/                 # Original CICIoT2023 CSV files
│   └── processed/           # Prepared samples and SQLite upload history
├── models/                  # Saved machine-learning models
├── reports/
│   ├── confusion_matrix.png
│   └── feature_importance.png
├── src/
│   ├── prepare_data.py      # Creates labelled training and test samples
│   ├── train_model.py       # Trains and evaluates the classifier
│   └── plot_results.py      # Creates evaluation charts
├── static/
│   └── style.css
└── templates/
    ├── history.html
    ├── index.html
    └── results.html
```

## Setup

Open a terminal in the project folder. Activate the virtual environment if needed:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Prepare the data

```powershell
python .\src\prepare_data.py
```

This creates:

```text
data/processed/ids_multiclass.csv
```

## Train and evaluate the model

```powershell
python .\src\train_model.py
```

This saves the trained model to:

```text
models/ids_random_forest_multiclass.joblib
```

## Create the charts

```powershell
python .\src\plot_results.py
```

This creates:

```text
reports/confusion_matrix.png
reports/feature_importance.png
```

## Run the dashboard

```powershell
python .\app.py
```

Open this address in a browser:

```text
http://127.0.0.1:5000
```

Upload a CSV file containing the numeric feature columns used by the model. The dashboard displays predicted classes, an alert summary, and a preview of predictions. Successful analyses are recorded in:

```text
data/processed/ids_history.db
```

Stop the local server with **Ctrl+C** in the terminal.

## Limitations

- The dashboard classifies uploaded CSV files; it does not capture live network traffic.
- The model predicts only the four classes listed above. Other traffic may be assigned to one of them.
- Evaluation uses held-out files from CICIoT2023. Results on other networks or datasets may differ.
- The dashboard alert reflects model predictions, not a verified security incident.