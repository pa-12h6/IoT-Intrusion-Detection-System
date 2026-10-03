from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "CSV"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "ids_multiclass.csv"

# For each class, files 0, 1, and 2 are used for training.
# File 3 is held out for testing.
CLASS_FILES = {
    "Benign": ("Benign_Final", "BenignTraffic"),
    "DDoS-UDP_Flood": ("DDoS-UDP_Flood", "DDoS-UDP_Flood"),
    "DoS-UDP_Flood": ("DoS-UDP_Flood", "DoS-UDP_Flood"),
    "Mirai-udpplain": ("Mirai-udpplain", "Mirai-udpplain"),
    "DDoS-ICMP_Flood": ("DDoS-ICMP_Flood", "DDoS-ICMP_Flood"),
    "DDoS-TCP_Flood": ("DDoS-TCP_Flood", "DDoS-TCP_Flood"),
    "DDoS-SYN_Flood": ("DDoS-SYN_Flood", "DDoS-SYN_Flood"),
    "Mirai-greeth_flood": ("Mirai-greeth_flood", "Mirai-greeth_flood"),
    "DoS-SYN_Flood": ("DoS-SYN_Flood", "DoS-SYN_Flood"),
}

SAMPLES_PER_FILE = 3_000
RANDOM_STATE = 42
samples = []

for label, (folder_name, file_prefix) in CLASS_FILES.items():
    for file_number, split in [
        ("", "train"),
        ("1", "train"),
        ("2", "train"),
        ("3", "test"),
    ]:
        filename = f"{file_prefix}{file_number}.pcap.csv"
        csv_path = DATA_ROOT / folder_name / filename

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {csv_path}\n"
                "Check the folder and filename in VS Code Explorer."
            )

        print(f"Reading {filename} ({label}, {split})...")
        data = pd.read_csv(csv_path)

        sample_size = min(SAMPLES_PER_FILE, len(data))
        data = data.sample(n=sample_size, random_state=RANDOM_STATE)
        data["Label"] = label
        data["SourceFile"] = filename
        data["Split"] = split
        samples.append(data)

        print(f"  Selected {sample_size:,} rows")

combined = pd.concat(samples, ignore_index=True)

metadata_columns = ["Label", "SourceFile", "Split"]
feature_columns = combined.columns.drop(metadata_columns)

combined[feature_columns] = combined[feature_columns].replace(
    [float("inf"), float("-inf")],
    pd.NA,
)

rows_before = len(combined)
combined = combined.dropna()
print(f"Removed {rows_before - len(combined)} rows with invalid values.")

combined = combined.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(OUTPUT_FILE, index=False)

print(f"\nSaved {len(combined):,} rows to:")
print(OUTPUT_FILE)
print("\nRows by split and label:")
print(combined.groupby(["Split", "Label"]).size().to_string())