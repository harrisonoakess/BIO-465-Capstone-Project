import argparse
import json
import csv
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

from output_parsing_to_csv import get_input_file_names, get_predictions
from generate_plots import make_plot_folder

ref_file_path = Path(__file__).parent.parent.resolve() / "prep_files" / "output_files" / "control_proteins.csv"
control_output_path = Path(__file__).parent.resolve() / "control_outputs"

def scatter_plot_experimental_vs_predicted(data, output_file, log_scale=False):
    predicted_affinity_field = 'micromolar_affinity_pred_value'
    experimental_affinity_field = 'Experimental_Affinity'

    x = data[experimental_affinity_field]
    y = data[predicted_affinity_field]

    plt.scatter(x, y, alpha=0.5)

    if log_scale:
        result = linregress(np.log10(x), np.log10(y))
        m = result.slope
        b = result.intercept
        r2 = result.rvalue ** 2

        x_line = np.geomspace(x.min(), x.max(), 300)
        y_line = (10 ** b) * (x_line ** m)

        plt.plot(x_line, y_line, color='red', 
                 linewidth=2, 
                 label=f"Fit: y={10**b:.2f}x^{m:.2f}, R^2={r2:.3f}")

        plt.xscale('log')
        plt.yscale('log')
        plt.title("Experimental vs Predicted Affinity (uM, log-log scale)")

    else:
        result = linregress(x, y)
        m = result.slope
        b = result.intercept
        r2 = result.rvalue ** 2

        x_line = np.linspace(x.min(), x.max(), 300)
        y_line = m * x_line + b

        plt.plot(x_line, y_line, color='red', 
                 linewidth=2, 
                 label=f"Fit: y={m:.2f}x+{b:.2f}, R^2={r2:.3f}")
        
        plt.title("Experimental vs Predicted Affinity (uM)")

    plt.legend()
    plt.xlabel("Experimental Affinity (uM)")
    plt.ylabel("Predicted Affinity (uM)")
    plt.savefig(output_file)
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--input_folder", type=str, required=True)
    ap.add_argument("--input_folder", type=str, default="control_tests")
    args = ap.parse_args()

    reference_data = pd.read_csv(ref_file_path)
    file_names = get_input_file_names(args.input_folder)

    confidence_list = get_predictions(args.input_folder, file_names, batched_outputs=False)

    confidence_df = pd.DataFrame(confidence_list)

    combined_data = pd.merge(
        confidence_df,
        reference_data,
        left_on=["protein", "ligand"],
        right_on=["PDB", "ligand_id"],
        how="left",
    )

    combined_data = combined_data.drop_duplicates(subset=["protein", "ligand", "micromolar_affinity_pred_value", "Experimental_Affinity"])

    print(f'Found {len(combined_data)} unique protein-ligand pairs')

    script_loc = Path(__file__).parent.resolve()
    target_loc = script_loc.parent.resolve() / "processed_data"

    csv_file = target_loc / f"confidence_predictions_{args.input_folder}.csv"

    combined_data.to_csv(csv_file, index=False)

    plot_folder = make_plot_folder(args.input_folder)
    scatter_plot_experimental_vs_predicted(combined_data, 
                                           plot_folder / f"scatter_plot_{args.input_folder}.png")
    scatter_plot_experimental_vs_predicted(combined_data, 
                                           plot_folder / f"log_scatter_plot_{args.input_folder}.png", 
                                           log_scale=True)

if __name__ == "__main__":
    main()
