from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "model_comparison.csv"
CHART_FILE = PROJECT_ROOT / "reports" / "model_comparison.png"

comparison = pd.read_csv(REPORT_FILE)

models = comparison["Model"]
positions = range(len(models))
bar_width = 0.36

fig, ax = plt.subplots(figsize=(10, 6))

accuracy_bars = ax.bar(
    [position - bar_width / 2 for position in positions],
    comparison["Accuracy"],
    bar_width,
    label="Accuracy",
    color="#1769aa",
)

f1_bars = ax.bar(
    [position + bar_width / 2 for position in positions],
    comparison["Macro F1"],
    bar_width,
    label="Macro F1",
    color="#52a675",
)

ax.set_title("Classifier Performance Comparison")
ax.set_ylabel("Score")
ax.set_xticks(list(positions))
ax.set_xticklabels(models, rotation=15, ha="right")
ax.set_ylim(0, 1.08)
ax.legend()
ax.grid(axis="y", alpha=0.25)

for bars in (accuracy_bars, f1_bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.3f}",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            fontsize=8,
        )

fig.tight_layout()
CHART_FILE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(CHART_FILE, dpi=180)
plt.close(fig)

print(f"Saved model comparison chart to: {CHART_FILE}")