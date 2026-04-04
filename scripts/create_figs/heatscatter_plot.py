import os
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from pathlib import Path
from pyrolite.plot import pyroplot

# PROJECT_ROOT = Path(os.environ["PROJECT_ROOT"])
# SCRIPT_DIR = Path(os.environ["SCRIPT_DIR"])
# YAML_DIR = Path(os.environ["YAML_DIR"])
# OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
PROCESSED_DIR = Path(os.environ["PROCESSED_DIR"])
PLOT_DIR = Path(os.environ["PLOT_DIR"])

def load_csv_data(csv_file: str):
    csv_file_path = PROCESSED_DIR / csv_file
    
    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    data = pd.read_csv(csv_file_path)
    return data

def create_heat_scatter_plot(data: pd.DataFrame, ligand_name_1: str, ligand_name_2: str, log_scale: bool = False):
    x_col = f"{ligand_name_1}_micromolar_affinity_pred_value"
    y_col = f"{ligand_name_2}_micromolar_affinity_pred_value"

    x = data[x_col]
    y = data[y_col]

    fig, ax = plt.subplots(figsize=(12, 8))

    data.pyroplot.heatscatter(s=5, ax=ax)

    # sns.scatterplot(x=x, y=y, alpha=0.6, c=density)
    # sns.jointplot(x=x, y=y, kind="hex", cmap='viridis')
    # ax.set_xlabel(f"{ligand_name_1} Predicted Affinity (µM)")
    # ax.set_ylabel(f"{ligand_name_2} Predicted Affinity (µM)")
    
    ax.set_xlabel(f"C16 Predicted Affinity (µM)")
    ax.set_ylabel(f"C16 Dihydro Predicted Affinity (µM)")
    ax.grid(True)
    # ax.tight_layout()

    # # Add X = Y line for reference
    # max_val = max(x.max(), y.max())
    # ax.plot([0, max_val], [0, max_val], color='red',
    #             linestyle='solid', label='X = Y')
    
    if log_scale:
        slope, intercept, r_value, p_value, std_err = linear_regression(np.log10(x), np.log10(y))
        m = slope
        b = intercept
        r2 = r_value ** 2
        
        ax.set_xscale('log')
        ax.set_yscale('log')

        x_line = np.geomspace(x.min(), x.max(), 300)
        y_line = (10 ** b) * (x_line ** m)

        ax.plot(x_line, y_line, color='blue', 
                 linestyle='dashed', linewidth=2, 
                 label=f"Fit: y={10**b:.2f}x^{m:.2f}, R^2={r2:.3f}")

        # ax.title("Experimental vs Predicted Affinity (uM, log-log scale)")
        ax.set_title("Heat Scatter Plot of Predicted Affinities (log-log scale)")
        plot_title = f"heat_scatter_{ligand_name_1}_vs_{ligand_name_2}_log.png"


    else:
        slope, intercept, r_value, p_value, std_err = linear_regression(x, y)
        m = slope
        b = intercept
        r2 = r_value ** 2

        x_line = np.linspace(x.min(), x.max(), 300)
        y_line = m * x_line + b

        ax.plot(x_line, y_line, color='blue', 
                 linestyle='dashed', linewidth=2, 
                 label=f"Fit: y={m:.2f}x+{b:.2f}, R^2={r2:.3f}")
        
        # ax.title("Experimental vs Predicted Affinity (uM)")
        ax.set_title("Heat Scatter Plot of Predicted Affinities")
        plot_title = f"heat_scatter_{ligand_name_1}_vs_{ligand_name_2}.png"

    ax.text(
        0.05, 0.95,
        f"$R^2$ = {r2:.3f}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=14,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="none")
    )

    # ax.legend(loc="best")
    plot_file_path = PLOT_DIR / plot_title
    plt.savefig(plot_file_path, bbox_inches='tight', dpi=300)
    print(f"Heat scatter plot saved to: {plot_file_path}")
    plt.show()

def linear_regression(x, y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    return slope, intercept, r_value, p_value, std_err

def main():
    # This script makes a heat scatter plot showing the affinity predictions for two different
    # ligands on a set of proteins. Each point corresponds to a protein and the X/Y coordinates
    # correspond to predicted affinity

    # It assumes two CSV files, each run with a different ligand, but same set of proteins
    # The CSV file names are specified with --csvs
    # The --ligand_names argument can be used to label the ligands for the two CSVs
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--csvs", type=str, nargs=2, 
                    default=["confidence_predictions_random_plus_pauls_c16.csv", "confidence_predictions_random_plus_paul_c16dihydro.csv"])
    ap.add_argument("--ligand_names", type=str, nargs=2, 
                    default=["c16", "c16_dihydro"])
    args = ap.parse_args()

    file_name_1, file_name_2 = args.csvs
    ligand_name_1, ligand_name_2 = args.ligand_names

    data_1 = load_csv_data(file_name_1)
    data_2 = load_csv_data(file_name_2)

    affinity_col = "micromolar_affinity_pred_value"
    target_cols = ["protein", affinity_col]

    data_1 = data_1[target_cols]
    data_2 = data_2[target_cols]

    data_1 = data_1.rename(columns={affinity_col: f"{ligand_name_1}_{affinity_col}"})
    data_2 = data_2.rename(columns={affinity_col: f"{ligand_name_2}_{affinity_col}"})

    merged_data = pd.merge(data_1, data_2, on="protein")
    merged_data = merged_data.drop("protein", axis=1)

    create_heat_scatter_plot(merged_data, ligand_name_1, ligand_name_2)
    create_heat_scatter_plot(merged_data, ligand_name_1, ligand_name_2, log_scale=True)


if __name__ == "__main__":
    main()