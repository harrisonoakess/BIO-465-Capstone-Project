import os
import csv
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from pathlib import Path

# PROJECT_ROOT = Path(os.environ["PROJECT_ROOT"])
# SCRIPT_DIR = Path(os.environ["SCRIPT_DIR"])
# YAML_DIR = Path(os.environ["YAML_DIR"])
# OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
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


def create_box_plot(data: pd.DataFrame, plot_name: str):

    affinity_field = "neg_log_molar_affinity_pred_value"

    data = data[data["protein_category"].isin(["Target Proteins", "Random Proteins"])]

    all_proteins_data = data[data["protein_category"] == "Random Proteins"]
    target_proteins_data = data[data["protein_category"] == "Target Proteins"]

    all_proteins_affinity = all_proteins_data[affinity_field]
    target_proteins_affinity = target_proteins_data[affinity_field]

    plot_title = "C16 Affinity Predictions for Target vs Random Proteins"

    plt.figure(figsize=(10, 6))
    sns.boxplot(x="protein_category", y=affinity_field, data=data, palette="Set2")
    plt.title(plot_title)
    plt.xlabel("Protein Category")
    plt.ylabel("Predicted Affinity (-log10 M)")


    plot_file_path = PLOT_DIR / plot_name
    plt.savefig(plot_file_path, bbox_inches='tight')
    print(f"Box plot saved to: {plot_file_path}")
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proteins_of_interest_csv", type=str, nargs='+', default=["human_pisa_proteins.csv"])
    ap.add_argument("--all_proteins_csv", type=str, nargs='+', default=["2000_random_proteins.csv"])
    ap.add_argument("--processed_csv", type=str, nargs='+', default=["confidence_predictions_pisa_c16_human.csv",
                                                                     "confidence_predictions_random_plus_pauls_c16.csv"])
    args = ap.parse_args()

    proteins_of_interest_list = args.proteins_of_interest_csv
    all_proteins_list = args.all_proteins_csv
    processed_csv_list = args.processed_csv

    target_proteins = set()

    for proteins_csv in proteins_of_interest_list:
        target_proteins.update(read_proteins_from_source(proteins_csv))

    all_proteins = set()

    for all_proteins_csv in all_proteins_list:
        all_proteins.update(read_proteins_from_source(all_proteins_csv))

    print(f'Number of target proteins: {len(target_proteins)}')
    print(f'Number of random proteins: {len(all_proteins)}')

    all_confidence_data = []

    for processed_csv in processed_csv_list:
        confidence_data = load_processed_csv_data(processed_csv)
        all_confidence_data.append(confidence_data)

    all_confidence_df = pd.concat(all_confidence_data, ignore_index=True)

    all_confidence_df["protein_category"] = all_confidence_df["protein"].apply(lambda x: "Target Proteins" if x in target_proteins else ("Random Proteins" if x in all_proteins else "Unknown Proteins"))
    
    create_box_plot(all_confidence_df, 'c16_pisa_boxplot.png')


if __name__ == "__main__":
    main()