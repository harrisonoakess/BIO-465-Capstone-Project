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

def load_csv_data(csv_file: str):
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


def create_box_plot(data: pd.DataFrame, plot_name: str, statistical_note: str = ""):
    affinity_field = "neg_log_molar_affinity_pred_value"
    plot_title = "C16 and C16 Dihydro Affinity Predictions for PISA Proteins"

    plt.figure(figsize=(10, 6))
    sns.boxplot(x="ligand_category", y=affinity_field, data=data, palette="Set2")
    plt.title(plot_title)
    plt.xlabel("Ligand Category")
    plt.ylabel("Predicted Affinity (-log10 M)")
    
    if statistical_note:
        plt.text(0.65, 0.95, statistical_note, 
                 transform=plt.gca().transAxes, 
                 verticalalignment='top', 
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plot_file_path = PLOT_DIR / plot_name
    plt.savefig(plot_file_path, bbox_inches='tight')
    print(f"Box plot saved to: {plot_file_path}")
    plt.show()

def wilcoxon_test(x, y):
    stat, p_value = stats.wilcoxon(x, y)
    return stat, p_value

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csvs", type=str, nargs=2, 
                    default=["confidence_predictions_pisa_c16_human.csv", "confidence_predictions_pisa_c16dihydro.csv"])
    ap.add_argument("--ligand_names", type=str, nargs=2, 
                    default=["c16", "c16_dihydro"])
    args = ap.parse_args()

    file_name_1, file_name_2 = args.csvs
    ligand_name_1, ligand_name_2 = args.ligand_names

    clean_ligand_name_1 = ligand_name_1.replace("_", " ").title()
    clean_ligand_name_2 = ligand_name_2.replace("_", " ").title()

    data_1 = load_csv_data(file_name_1)
    data_2 = load_csv_data(file_name_2)

    affinity_col = "neg_log_molar_affinity_pred_value"
    target_cols = ["protein", affinity_col]

    data_1 = data_1[target_cols]
    data_2 = data_2[target_cols]

    data_1 = data_1.assign(ligand_category=clean_ligand_name_1)
    data_2 = data_2.assign(ligand_category=clean_ligand_name_2)

    paired_data = pd.merge(data_1, data_2, on="protein", suffixes=(f"_{clean_ligand_name_1}", f"_{clean_ligand_name_2}"))
    
    paired_data = paired_data.drop("protein", axis=1)

    aff_1 = paired_data[f"{affinity_col}_{clean_ligand_name_1}"]
    aff_2 = paired_data[f"{affinity_col}_{clean_ligand_name_2}"]

    stat, p_value = wilcoxon_test(aff_1, aff_2)
    print(f"Wilcoxon test statistic: {stat}, p-value: {p_value}")

    statistical_note = f"Wilcoxon test p-value: {p_value:.3e}"

    merged_data = pd.concat([data_1, data_2], ignore_index=True)

    create_box_plot(merged_data, 'pisa_c16_c16dihydro_boxplot.png', statistical_note)


if __name__ == "__main__":
    main()