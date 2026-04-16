import os
import csv
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from pathlib import Path

PROCESSED_DIR = Path(os.environ["PROCESSED_DIR"])
PLOT_DIR = Path(os.environ["PLOT_DIR"])
SOURCE_DIR = Path(os.environ["SOURCE_DIR"])

def load_processed_csv_data(csv_file: str):
    csv_file_path = PROCESSED_DIR / csv_file
    
    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    data = pd.read_csv(csv_file_path)
    return data

def read_proteins_from_source(file_name: str):
    proteins = set()
    csv_path = SOURCE_DIR / file_name
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = (row.get("accession") or "").strip()
            if acc:
                proteins.add(acc)
    return proteins


def create_histogram(data: pd.DataFrame, plot_name: str, plot_title: str):

    affinity_field = "neg_log_molar_affinity_pred_value"
    affinity_vals = data[affinity_field]

    plt.figure(figsize=(10, 6))
    sns.histplot(affinity_vals, bins=30, kde=True, color="skyblue")
    plt.title(plot_title)
    plt.xlabel("Predicted Affinity (-log10 M)")
    plt.ylabel("Count")

    plot_file_path = PLOT_DIR / plot_name
    plt.savefig(plot_file_path, bbox_inches='tight')
    print(f"Histogram saved to: {plot_file_path}")
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed_csv", type=str, nargs='+', default=["confidence_predictions_pisa_c16_human.csv",
                                                                    "confidence_predictions_pisa_c16dihydro.csv"])
    ap.add_argument("--ligand_name", type=str, default=["C16", "C16 Dihydro"])
    args = ap.parse_args()

    processed_csv_list = args.processed_csv
    ligand_name_list = args.ligand_name

    for csv_file, ligand_name in zip(processed_csv_list, ligand_name_list):
        data = load_processed_csv_data(csv_file)
        plot_name = f"{ligand_name.lower().replace(' ', '_')}_affinity_distribution.png"
        plot_title = f"{ligand_name} Affinity Distribution for PISA Proteins"
        create_histogram(data, plot_name, plot_title)


if __name__ == "__main__":
    main()
