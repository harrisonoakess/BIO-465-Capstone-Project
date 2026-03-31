import pandas as pd
import numpy as np
import argparse
import gseapy as gp
from mygene import MyGeneInfo
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


def get_good_binders(df, affinity_col, method="percentile", value=0.1, absolute_cutoff=None):
    """
    Select top binders based on affinity score (-log10 already applied).
    - Percentile method: selects top x% of strongest binders (highest scores)
    - Absolute method: selects binders above a threshold
    Returns subset dataframe and cutoff value.
    """
    if method == "percentile":
        cutoff = df[affinity_col].quantile(1 - value)  # higher = stronger
        good = df[df[affinity_col] >= cutoff]
    elif method == "absolute":
        if absolute_cutoff is None:
            raise ValueError("absolute_cutoff must be provided for absolute method")
        cutoff = absolute_cutoff
        good = df[df[affinity_col] >= absolute_cutoff]
    else:
        raise ValueError("method must be 'percentile' or 'absolute'")
    return good, cutoff


def map_to_gene_symbols(accessions):
    mg = MyGeneInfo()
    results = mg.querymany(
        accessions,
        scopes="uniprot",
        fields="symbol",
        species=9606
    )
    mapping = {r["query"]: r["symbol"] for r in results if "symbol" in r and "query" in r}
    return mapping


def run_enrichment(protein_list, outdir):
    enr = gp.enrichr(
        gene_list=protein_list,
        gene_sets=[
            "GO_Biological_Process_2021",
            "GO_Molecular_Function_2021",
            "KEGG_2021_Human"
        ],
        organism="homo sapiens",
        outdir=str(outdir),
        cutoff=0.05,   
        no_plot=True
    )
    return enr


def plot_top_enrichment(results, outdir, p, top_n=15, x_col="Combined Score"):
    """
    Plot top enriched pathways.
    
    Parameters:
    - results: Enrichr results dataframe
    - outdir: folder to save the plot
    - top_n: number of top terms to plot
    - x_col: which column to plot on x-axis; options include:
        "Combined Score" (default), "Adjusted P-value", "Overlap", "Enrichment Ratio"
    """    
    if results is None or results.empty:
        print("No enrichment results to plot.")
        return

    results_sorted = results.sort_values("Adjusted P-value").head(top_n)

    # For FDR, take -log10 or higher = more significant
    if x_col.lower() in ["adjusted p-value", "fdr"]:
        results_sorted["neg_log10_fdr"] = -np.log10(results_sorted["Adjusted P-value"])
        x_col = "neg_log10_fdr"

    # Sort descending by chosen metric
    results_sorted = results_sorted.sort_values(x_col, ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=results_sorted,
        y="Term",
        x=x_col,
        palette="viridis"
    )

    # Threshold line for FDR, 1.3 is about 0.05 significance
    if x_col == "neg_log10_fdr":
        plt.axvline(x=1.3, color='red', linestyle='--', linewidth=1)
        plt.text(1.32, plt.ylim()[1]*0.95, "FDR = 0.05", color='red', fontsize=10)

    xlabel_map = {
        "Combined Score": "Combined Score",
        "neg_log10_fdr": "-log10(FDR)",
        "Enrichment Ratio": "Enrichment Ratio",
        "Overlap": "Gene Count"
    }

    plt.xlabel(xlabel_map.get(x_col, x_col))
    plt.ylabel("")
    plt.title(f"Pathway Enrichment (Top {int(p*100)}% Predicted Binders)")
    plt.tight_layout()
    plt.savefig(outdir / f"top_enrichment_barplot_{x_col.replace(' ', '_')}.png")
    plt.close()
    print(f"Saved barplot to top_enrichment_barplot_{x_col.replace(' ', '_')}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--affinity_col", default="neg_log_molar_affinity_pred_value")
    parser.add_argument("--method", choices=["percentile", "absolute"], default="percentile")
    parser.add_argument("--percentiles", nargs="+", type=float, default=[0.01, 0.05, 0.10])
    parser.add_argument("--absolute_cutoff", type=float, default=None)
    parser.add_argument("--x_col", default="Combined Score")
    parser.add_argument("--group_map", required=True, help="CSV mapping proteins to groups")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.csv)

    # Load group mapping
    group_df = pd.read_csv(args.group_map)

    # Merge with main dataframe
    df = df.merge(group_df, on="protein", how="left")

    # Drop proteins without group assignment
    df = df.dropna(subset=["group"])
    print(f"Groups found: {df['group'].unique()}")

    # Create output folder based on CSV name after "predictions_"
    csv_name = Path(args.csv).stem
    folder_name = csv_name.split("predictions_")[-1]
    outdir = Path("../enrichment_analysis") / folder_name
    outdir.mkdir(parents=True, exist_ok=True)

    # Loop over biological groups
    for group_name, subset_df in df.groupby("group"):
        print(f"\n===== Processing group: {group_name} =====")

        for p in args.percentiles:
            print(f"\nProcessing top {int(p*100)}% binders...")
            
            good_df, cutoff = get_good_binders(
                subset_df,
                affinity_col=args.affinity_col,
                method=args.method,
                value=p,
                absolute_cutoff=args.absolute_cutoff
            )

            print(f"Cutoff used: {cutoff}")
            print(f"Number of good binders: {len(good_df)}")

            gene_list = good_df["gene_symbol"].dropna().unique().tolist()
            print(f"Mapped to {len(gene_list)} gene symbols")

            if len(gene_list) == 0:
                print("No valid gene symbols found. Skipping.")
                continue

            # Group-specific output folder
            percentile_outdir = outdir / group_name / f"top_{int(p*100)}pct"
            percentile_outdir.mkdir(parents=True, exist_ok=True)

            print("Running enrichment...")
            enr = run_enrichment(gene_list, percentile_outdir)

            results = enr.results
            if results is None or results.empty:
                print("No enrichment results found.")
            else:
                results_sorted = results.sort_values("Adjusted P-value")
                results_sorted.to_csv(
                    percentile_outdir / f"enrichment_{group_name}_top_{int(p*100)}pct.csv",
                    index=False
                )

                plot_top_enrichment(
                    results_sorted,
                    percentile_outdir,
                    p,
                    top_n=20,
                    x_col=args.x_col
                )

if __name__ == "__main__":
    main()