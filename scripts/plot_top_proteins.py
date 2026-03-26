import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_top_binders(df, affinity_col, method, value):
    if method == "top_n":
        return df.nsmallest(value, affinity_col)
    
    elif method == "percentile":
        cutoff = df[affinity_col].quantile(value)
        return df[df[affinity_col] <= cutoff]
    
    elif method == "threshold":
        return df[df[affinity_col] <= value]
    
    else:
        raise ValueError("Invalid method")

def plot_ranked_binders(df, protein_col, affinity_col, ligand_col, output_file):
    # Sort by affinity (lower = better)
    df_sorted = df.sort_values(by=affinity_col, ascending=True)

    plt.figure(figsize=(10, 6))

    ax = sns.barplot(
        data=df_sorted,
        x=affinity_col,
        y=protein_col,
        # hue="ligand" if not ligand_col else None,
        palette="viridis"
    )

    # # Add value labels (annotations)
    # for i, row in df_sorted.iterrows():
    #     ax.text(
    #         row[affinity_col],
    #         i,
    #         f"{row[affinity_col]:.2e}",
    #         va='center'
    #     )

    plt.xlabel("Affinity")
    plt.ylabel("Protein")
    plt.title("Top 20 Ranked Protein Binding Affinities")
    plt.tight_layout()

    plt.savefig(output_file)
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--ligand", default=None, help="Ligand name (optional)")
    
    parser.add_argument("--method", choices=["top_n", "percentile", "threshold"], required=True)
    parser.add_argument("--value", type=int, required=True)
    parser.add_argument("--affinity_col", default="micromolar_affinity_pred_value")

    parser.add_argument("--output", default="top_binders.png")

    args = parser.parse_args()

    df = pd.read_csv(args.csv)

    affinity_col = args.affinity_col
    ligand_col = args.ligand

    # Optional ligand filtering
    if args.ligand:
        df = df[df["ligand"] == args.ligand]

    if df.empty:
        print("No data after filtering.")
        return

    # Get top binders
    top_df = get_top_binders(df, affinity_col, args.method, args.value)

    if top_df.empty:
        print("No proteins meet the threshold.")
        return

    # Sort for plotting
    top_df = top_df.sort_values(by=affinity_col)

    # Plot
    plot_ranked_binders(top_df, protein_col="protein", affinity_col=affinity_col, ligand_col=ligand_col, 
    output_file=args.output)

    # plt.figure(figsize=(10, 6))
    # sns.barplot(
    #     data=top_df,
    #     x=affinity_col,
    #     y="protein",
    #     hue="ligand" if not args.ligand else None,
    #     dodge=False
    # )

    # plt.title("Top Protein Binders")
    # plt.xlabel("Affinity (micromolar, lower = better)")
    # plt.ylabel("Protein")
    # plt.tight_layout()

    # plt.savefig(args.output)
    # plt.close()
    print(f"Saved plot to {args.output}")


if __name__ == "__main__":
    main()