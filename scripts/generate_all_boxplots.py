import os
import csv
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from pathlib import Path

# Environment folders
PROCESSED_DIR = Path(os.environ["PROCESSED_DIR"])
PLOT_DIR = Path(os.environ["PLOT_DIR"])
SOURCE_DIR = Path(os.environ["SOURCE_DIR"])

def load_csv(csv_file: str):
    csv_path = PROCESSED_DIR / csv_file
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    return pd.read_csv(csv_path)

def load_protein_list(file_name: str):
    proteins = set()
    csv_path = SOURCE_DIR / file_name
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = (row.get("accession") or "").strip()
            if acc:
                proteins.add(acc)
    return proteins

def categorize_proteins(df: pd.DataFrame, target_proteins: set, random_proteins: set):
    df["protein_category"] = df["protein"].apply(
        lambda x: "Target Proteins" if x in target_proteins else ("Random Proteins" if x in random_proteins else "Unknown Proteins")
    )
    return df

def create_box_plot(df: pd.DataFrame, plot_name: str, plot_title: str, affinity_col="neg_log_molar_affinity_pred_value", show_stats=True):
    df = df[df["protein_category"].isin(["Target Proteins", "Random Proteins"])]
    
    target_data = df[df["protein_category"] == "Target Proteins"][affinity_col]
    random_data = df[df["protein_category"] == "Random Proteins"][affinity_col]

    if show_stats:
        t_stat, p_value = stats.ttest_ind(random_data, target_data, equal_var=False)
        print(f"T-test: t-stat={t_stat:.2f}, p-value={p_value:.5f}")
    else:
        p_value = None

    plt.figure(figsize=(10, 6))
    sns.boxplot(x="protein_category", y=affinity_col, data=df, palette="Set2")
    plt.title(plot_title)
    plt.xlabel("Protein Category")
    plt.ylabel(f"Predicted Affinity (-log10 M)")

    if show_stats and p_value is not None:
        plt.text(0.05, 0.95, f"P-value={p_value:.5f}", transform=plt.gca().transAxes, va="top", ha="left", fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(PLOT_DIR / plot_name, bbox_inches='tight')
    print(f"Box plot saved: {PLOT_DIR / plot_name}")
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_csvs", type=str, nargs='+', required=True, help="CSV(s) with target proteins")
    parser.add_argument("--random_csvs", type=str, nargs='+', required=True, help="CSV(s) with random proteins")
    parser.add_argument("--processed_csvs", type=str, nargs='+', required=True, help="CSV(s) with predictions")
    parser.add_argument("--by_ligand", action="store_true", help="Create separate boxplots per ligand")
    parser.add_argument("--affinity_col", type=str, default="neg_log_molar_affinity_pred_value")
    parser.add_argument("--show_stats", action="store_true", help="Compute and display T-test")
    args = parser.parse_args()

    # Load proteins
    target_proteins = set()
    for f in args.target_csvs:
        target_proteins.update(load_protein_list(f))

    random_proteins = set()
    for f in args.random_csvs:
        random_proteins.update(load_protein_list(f))

    print(f"Target proteins: {len(target_proteins)}, Random proteins: {len(random_proteins)}")

    # Load prediction data
    all_df = pd.concat([load_csv(f) for f in args.processed_csvs], ignore_index=True)
    all_df = categorize_proteins(all_df, target_proteins, random_proteins)

    # Plotting
    if args.by_ligand and "ligand" in all_df.columns:
        for ligand in all_df["ligand"].unique():
            ligand_df = all_df[all_df["ligand"] == ligand]
            plot_name = f"{ligand.lower().replace(' ','_')}_boxplot.png"
            plot_title = f"{ligand} - Affinity Predictions"
            create_box_plot(ligand_df, plot_name, plot_title, affinity_col=args.affinity_col, show_stats=args.show_stats)
    else:
        create_box_plot(all_df, "all_proteins_boxplot.png", "All Proteins - Affinity Predictions", affinity_col=args.affinity_col, show_stats=args.show_stats)

if __name__ == "__main__":
    main()