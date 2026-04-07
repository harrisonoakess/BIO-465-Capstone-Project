import pandas as pd
import argparse
import os 

def save_top_and_bottom(df, column, n, results_dir, protein_column, ligand_column):
    # Check if all columns are present
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in CSV.")
    if protein_column not in df.columns:
        raise ValueError(f"Protein ID column '{protein_column}' not found in CSV.")
    if ligand_column not in df.columns:
        raise ValueError(f"Ligand ID column '{ligand_column}' not found in CSV.")

    df_sorted = df.sort_values(by=column, ascending=False).reset_index(drop=True)

    # Get top n
    top = df_sorted.head(n)
    bottom = df_sorted.tail(n)

    # Save results
    output_folder = os.path.join("..", "outputs", "good_binders")
    os.makedirs(output_folder, exist_ok=True)
    top.to_csv(os.path.join(output_folder, "top_binders.csv"), index=False)
    bottom.to_csv(os.path.join(output_folder, "bottom_binders.csv"), index=False)

    print("Top proteins:")
    print(top)

    print("\nBottom proteins:")
    print(bottom)

    # Build file paths
    def build_paths(subset):
        paths = []
        for _, row in subset.iterrows():
            protein = row[protein_column]
            ligand = row[ligand_column]

            cif_path = os.path.join(
                results_dir,
                f"boltz_results_{protein}__{ligand}",
                "predictions",
                f"{protein}__{ligand}",
                f"{protein}__{ligand}_model_0.cif"
            )

            paths.append(cif_path)

        # filter valid
        valid = [p for p in paths if os.path.exists(p)]

        for p in paths:
            if not os.path.exists(p):
                print(f"Missing file: {p}")

        return valid

    # Get top and bottom files
    top_files = build_paths(top)
    bottom_files = build_paths(bottom)

    # Print files
    print("\nTOP FILES:")
    for f in top_files:
        print(f)

    print("\nBOTTOM FILES:")
    for f in bottom_files:
        print(f)

def read_csv(input_file):
    df = pd.read_csv(input_file)
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to target csv")
    parser.add_argument("--column", default="neg_log_molar_affinity_pred_value", help="Column to sort the data on from highest to lowest")
    parser.add_argument("--n", type=int, default=1, help="Number of top and bottom proteins to retrieve"
    )
    parser.add_argument("--results_dir", required=True, help="Directory containing boltz results and .cif files")
    parser.add_argument("--protein_column", default="protein", help="Column with protein IDs")
    parser.add_argument("--ligand_column", default="ligand", help="Column with ligand IDs")

    args = parser.parse_args()

    df = read_csv(args.csv)
    save_top_and_bottom(
        df, 
        args.column, 
        args.n,
        args.results_dir,
        args.protein_column,
        args.ligand_column
        )

if __name__ == "__main__":
    main()