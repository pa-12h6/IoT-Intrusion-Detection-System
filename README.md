# IoT Intrusion Detection System

A machine-learning project that classifies IoT network traffic from CSV feature files. It includes a Random Forest model and a Flask dashboard for uploading traffic files, viewing predictions, and reviewing upload history.

## Supported classes

The current model predicts four classes:

- Benign
- DDoS-UDP_Flood
- DoS-UDP_Flood
- Mirai-udpplain

## Project structure

```text
IoT-Intrusion-Detection-System/
├── app.py
├── data/
│   ├── raw/                 # Original CICIoT2023 CSV files
│   └── processed/           # Prepared samples and SQLite history
├── models/                  # Saved machine-learning models
├── reports/                 # Evaluation charts
├── src/
│   ├── prepare_data.py      # Creates labelled training and test samples
│   ├── train_model.py       # Trains and evaluates the classifier
│   └── plot_results.py      # Saves a confusion-matrix image
├── static/
│   └── style.css
└── templates/
    ├── history.html
    ├── index.html
    └── results.html
```

## Dataset

This project uses CSV feature files from the [CICIoT2023 dataset](https://www.unb.ca/cic/datasets/iotdataset-2023.html), provided by the Canadian Institute for Cybersecurity at the University of New Brunswick.

Place the extracted CSV category folders under:

```text
data/raw/CSV/
```

The current preparation script uses the Benign, DDoS-UDP_Flood, DoS-UDP_Flood, and Mirai-udpplain folders. It samples separate files for training and testing. Keep the original dataset files unchanged.

## Setup

Open a terminal in the project folder. Activate your virtual environment if it is not already active, then install the packages:

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

This saves the model to:

```text
models/ids_random_forest_multiclass.joblib
```

The current evaluation on held-out files achieved about 97% accuracy across the four supported classes. The main confusion was between DDoS-UDP_Flood and DoS-UDP_Flood. Results may vary with different samples and dataset files.

Create the confusion-matrix image with:

```powershell
python .\src\plot_results.py
```

The image is saved to:

```text
reports/confusion_matrix.png
```

## Run the dashboard

```powershell
python .\app.py
```

Open this address in a browser:

```text
http://127.0.0.1:5000
```

Upload a CSV file containing the numeric feature columns used by the trained model. The dashboard displays predicted classes, an alert summary, and a preview of predictions. Successful analyses are recorded in:

```text
data/processed/ids_history.db
```

Stop the local server with **Ctrl+C** in the terminal.

## Current limitations

- The dashboard classifies uploaded CSV files; it does not capture live network traffic.
- The model predicts only the four classes listed above. Other traffic may be assigned to one of them.
- Evaluation uses held-out files from CICIoT2023. Results on other networks or datasets may differ.
- The dashboard’s attack alert reflects model predictions, not a verified security incident.