import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path

def generate_global_scatter_plot(data, confidence_var, affinity_var, title, x_label, y_label, output_file):
    plt.figure(figsize=(10, 6))
    plt.scatter(data[confidence_var], data[affinity_var], alpha=0.5)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()
    plt.savefig(output_file)
    plt.close()

def generate_stereochemistry_sensitivity_plot(data, ligand1, ligand2, affinity_var, title, x_label, y_label, output_file):
    pivoted_data = data.pivot(index='protein', columns='ligand', values=affinity_var)

    plt.figure(figsize=(10, 6))
    plt.scatter(pivoted_data[ligand1], pivoted_data[ligand2], alpha=0.5)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()
    plt.savefig(output_file)
    plt.close()

def generate_heatmap(data, affinity_var, title, x_label, y_label, output_file):
    pivot_table = data.pivot(index='protein', columns='ligand', values=affinity_var)

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, annot=True, cmap='viridis')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(output_file)
    plt.close()

def make_plot_folder(csv_file_name):
    plot_folder = Path(__file__).parent.parent.resolve() / "plots" / csv_file_name.split('.')[0]
    if not plot_folder.exists():
        plot_folder.mkdir()
    return plot_folder

def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--csv", type=str, required=True)
    ap.add_argument("--csv", type=str, default="confidence_predictions_paul_with_NADPH.csv")
    args = ap.parse_args()

    protein_field = 'protein'
    ligand_field = 'ligand'    
    affinity_field = 'affinity_pred_value'

    csv_file_name = args.csv
    plot_folder = make_plot_folder(csv_file_name)

    data = pd.read_csv(Path(__file__).parent.parent.resolve() /
                    "processed_data" / csv_file_name)

    print(f"Data loaded from {csv_file_name}. Generating plots...")

    trimmed_csv_file_name = csv_file_name.split('.')[0]

    confidence_var = 'ligand_iptm'
    affinity_var = 'affinity_pred_value'

    generate_global_scatter_plot(data[[confidence_var, affinity_var]], 
                                 confidence_var, 
                                 affinity_var, 
                                 'Global Scatter Plot of Ligand iPTM vs Affinity', 
                                 'Ligand iPTM', 
                                 'Affinity', 
                                 plot_folder / f"global_scatter_{trimmed_csv_file_name}.png")

    ligand1 = 'N-Acetyl-beta-D-GLUCOSAMINE'
    ligand2 = 'N-Acetyl-D-Glucosamine'
    affinity_var = 'affinity_pred_value'

    generate_stereochemistry_sensitivity_plot(data[(data[ligand_field] == ligand1) |
                                                   (data[ligand_field] == ligand2)]
                                                   [[protein_field, ligand_field, affinity_field]], 
                                            ligand1, 
                                            ligand2, 
                                            affinity_var,
                                            'Stereochemistry Sensitivity Plot', 
                                            'N-Acetyl-beta-D-Glucosamine Affinity', 
                                            'N-Acetyl-D-Glucosamine Affinity', 
                                            plot_folder / 
                                            f"stereochemistry_sensitivity_{trimmed_csv_file_name}.png")

    affinity_var = 'affinity_pred_value'

    generate_heatmap(data[[protein_field, ligand_field, affinity_field]], 
                    affinity_var,
                    'Heatmap of Affinity by Protein and Ligand',
                    'Ligand',
                    'Protein',
                    plot_folder / f"heatmap_{trimmed_csv_file_name}.png")

    print(f'Plots saved to {plot_folder}')


if __name__ == "__main__":
    main()
