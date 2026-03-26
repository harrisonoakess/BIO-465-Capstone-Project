import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path("/uufs/chpc.utah.edu/common/home/u6073676/Capstone/BIO-465-Capstone-Project")
PROTEOME_FILE = PROJECT_ROOT / "prep_files" / "output_files" / "proteome.csv"
OUTPUT_BASE = PROJECT_ROOT / "processed_outputs" / "min_max"


def make_output_folder(csv_path):
    csv_stem = Path(csv_path).stem
    out_folder = OUTPUT_BASE / csv_stem
    out_folder.mkdir(parents=True, exist_ok=True)
    return out_folder


def add_protein_names(data, proteome_file):
    proteome_data = pd.read_csv(proteome_file)
    data = data.merge(
        proteome_data[["accession", "protein_name"]],
        left_on="protein",
        right_on="accession",
        how="left"
    )
    data.drop(columns=["accession"], inplace=True)
    return data


def generate_ligand_scatter_plot(data, confidence_var, affinity_var, ligand_label, output_folder):
    output_file = output_folder / f"{ligand_label}_scatter.png"

    plt.figure(figsize=(10, 6))
    plt.scatter(data[confidence_var], data[affinity_var], alpha=0.6, s=50)
    plt.title(f"{ligand_label}: Affinity vs Confidence")
    plt.xlabel("Confidence (ligand_iptm)")
    plt.ylabel("Predicted affinity (micromolar, lower = stronger)")
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Saved scatter plot: {output_file}")


def save_top_affinity_lists(data, protein_field, ligand_label, affinity_var, confidence_var, output_folder, top_x=10):
    strongest = data.sort_values(affinity_var, ascending=True).head(top_x).copy()
    weakest = data.sort_values(affinity_var, ascending=False).head(top_x).copy()

    keep_cols = ["protein", protein_field, "ligand", confidence_var, affinity_var]

    strongest_file = output_folder / f"{ligand_label}_strongest_{top_x}.csv"
    weakest_file = output_folder / f"{ligand_label}_weakest_{top_x}.csv"

    strongest.to_csv(strongest_file, index=False, columns=keep_cols)
    weakest.to_csv(weakest_file, index=False, columns=keep_cols)

    print(f"\n=== {ligand_label} ===")
    print(f"Saved strongest: {strongest_file}")
    print(f"Saved weakest:   {weakest_file}")

    print("\nStrongest predicted binders (lowest micromolar values):")
    print(strongest[keep_cols].to_string(index=False))

    print("\nWeakest predicted binders (highest micromolar values):")
    print(weakest[keep_cols].to_string(index=False))


def process_ligand(data, ligand_value, ligand_label, protein_field, confidence_var, affinity_var, output_folder, top_x=10):
    subset = data[data["ligand"] == ligand_value].copy()

    if subset.empty:
        print(f"No rows found for ligand: {ligand_value}")
        return

    subset[confidence_var] = pd.to_numeric(subset[confidence_var], errors="coerce")
    subset[affinity_var] = pd.to_numeric(subset[affinity_var], errors="coerce")
    subset = subset.dropna(subset=[confidence_var, affinity_var])

    generate_ligand_scatter_plot(
        subset,
        confidence_var,
        affinity_var,
        ligand_label,
        output_folder
    )

    save_top_affinity_lists(
        subset,
        protein_field,
        ligand_label,
        affinity_var,
        confidence_var,
        output_folder,
        top_x=top_x
    )


def resolve_csv_path(csv_arg):
    csv_path = Path(csv_arg)

    if csv_path.exists():
        return csv_path

    candidate1 = PROJECT_ROOT / "processed_outputs" / csv_arg
    if candidate1.exists():
        return candidate1

    candidate2 = PROJECT_ROOT / "processed_data" / csv_arg
    if candidate2.exists():
        return candidate2

    raise FileNotFoundError(
        f"Could not find CSV file '{csv_arg}' in current path, processed_outputs, or processed_data."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, required=True, help="CSV filename or full path")
    ap.add_argument("--top_x", type=int, default=10, help="Number of strongest/weakest proteins to save")
    args = ap.parse_args()

    protein_field = "protein_name"
    confidence_var = "ligand_iptm"
    affinity_var = "micromolar_affinity_pred_value"

    c16_ligand = "CER_d18_1_16_0_C16"
    c16dihydro_ligand = "CER_d18_0_16_0_C16"

    csv_path = resolve_csv_path(args.csv)
    output_folder = make_output_folder(csv_path)

    data = pd.read_csv(csv_path)

    print(f"Using proteome file: {PROTEOME_FILE}")
    data = add_protein_names(data, PROTEOME_FILE)

    print(f"Data loaded from {csv_path}")
    print(f"Saving outputs to {output_folder}")

    process_ligand(
        data,
        c16_ligand,
        "c16",
        protein_field,
        confidence_var,
        affinity_var,
        output_folder,
        top_x=args.top_x
    )

    process_ligand(
        data,
        c16dihydro_ligand,
        "c16dihydro",
        protein_field,
        confidence_var,
        affinity_var,
        output_folder,
        top_x=args.top_x
    )

    print(f"\nDone. Outputs saved to {output_folder}")


if __name__ == "__main__":
    main()