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

def generate_stereochemistry_sensitivity_plot(data, protein_var, ligand1, ligand2, affinity_var, title, x_label, y_label, output_file):
    pivoted_data = data.pivot(index=protein_var, columns='ligand', values=affinity_var)

    plt.figure(figsize=(10, 6))
    plt.scatter(pivoted_data[ligand1], pivoted_data[ligand2], alpha=0.5)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()
    plt.savefig(output_file)
    plt.close()

def generate_heatmap(data, protein_var, affinity_var, title, x_label, y_label, output_file):
    pivot_table = data.pivot(index=protein_var, columns='ligand', values=affinity_var)

    plt.figure(figsize=(14, 10))
    ax = sns.heatmap(pivot_table, 
                     annot=True, 
                     fmt='.0f', 
                     cmap='viridis_r')
    
    cbar = ax.collections[0].colorbar

    label_fs = 11
    cbar.ax.text(
        0.5, 1.025, "Low Affinity",
        ha="center", va="bottom",
        transform=cbar.ax.transAxes,
        fontsize=label_fs
    )
    cbar.ax.text(
        0.5, -0.025, "High Affinity",
        ha="center", va="top",
        transform=cbar.ax.transAxes,
        fontsize=label_fs
    )

    plt.title(title)
    plt.tight_layout()
    plt.xlabel("")
    plt.ylabel("")
    plt.savefig(output_file)
    plt.close()

def make_plot_folder(csv_file_name):
    plot_folder = Path(__file__).parent.parent.resolve() / "plots" / csv_file_name.split('.')[0]
    if not plot_folder.exists():
        plot_folder.mkdir()
    return plot_folder

def add_protein_names(data, proteome_file):
    proteome_data = pd.read_csv(proteome_file)
    data = data.merge(proteome_data[['accession', 'protein_name']], left_on='protein', right_on='accession', how='left')
    data.drop(columns=['accession'], inplace=True)
    return data

def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--csv", type=str, required=True)
    ap.add_argument("--csv", type=str, default="confidence_predictions_paul_with_NADPH.csv")
    args = ap.parse_args()

    protein_field = 'protein_name'
    ligand_field = 'ligand'    
    # affinity_field = 'affinity_pred_value'
    affinity_field = 'micromolar_affinity_pred_value'

    csv_file_name = args.csv
    plot_folder = make_plot_folder(csv_file_name)

    data = pd.read_csv(Path(__file__).parent.parent.resolve() /
                    "processed_data" / csv_file_name)

    proteome_file = Path(__file__).parent.parent.resolve() / "prep_files" / "output_files" / "proteome.csv"
    data = add_protein_names(data, proteome_file)

    print(f"Data loaded from {csv_file_name}. Generating plots...")

    trimmed_csv_file_name = csv_file_name.split('.')[0]

    confidence_var = 'ligand_iptm'
    # affinity_var = 'affinity_pred_value'
    affinity_var = 'micromolar_affinity_pred_value'

    generate_global_scatter_plot(data[[confidence_var, affinity_var]], 
                                 confidence_var, 
                                 affinity_var, 
                                 'Global Scatter Plot of Ligand iPTM vs Affinity', 
                                 'Ligand iPTM', 
                                 'Affinity (micromolar)', 
                                 plot_folder / f"global_scatter_{trimmed_csv_file_name}.png")

    ligand1 = 'N-Acetyl-beta-D-GLUCOSAMINE'
    ligand2 = 'N-Acetyl-D-Glucosamine'
    # affinity_var = 'affinity_pred_value'

    generate_stereochemistry_sensitivity_plot(data[(data[ligand_field] == ligand1) |
                                                   (data[ligand_field] == ligand2)]
                                                   [[protein_field, ligand_field, affinity_field]], 
                                            protein_field,
                                            ligand1, 
                                            ligand2, 
                                            affinity_var,
                                            'Stereochemistry Sensitivity Plot', 
                                            'N-Acetyl-beta-D-Glucosamine Affinity (micromolar)', 
                                            'N-Acetyl-D-Glucosamine Affinity (micromolar)', 
                                            plot_folder / 
                                            f"stereochemistry_sensitivity_{trimmed_csv_file_name}.png")

    # affinity_var = 'affinity_pred_value'

    generate_heatmap(data[[protein_field, ligand_field, affinity_field]], 
                    protein_field,
                    affinity_var,
                    'Heatmap of Affinity by Protein and Ligand',
                    'Ligand',
                    'Protein',
                    plot_folder / f"heatmap_{trimmed_csv_file_name}.png")

    print(f'Plots saved to {plot_folder}')


if __name__ == "__main__":
    main()
