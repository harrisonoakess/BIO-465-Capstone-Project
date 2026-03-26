import pandas as pd
import argparse
import gseapy as gp
from mygene import MyGeneInfo
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


def get_good_binders(df, affinity_col, method="percentile", value=0.1, absolute_cutoff=None):
    if method == "percentile":
        cutoff = df[affinity_col].quantile(value)
        good = df[df[affinity_col] <= cutoff]

    elif method == "absolute":
        if absolute_cutoff is None:
            raise ValueError("absolute_cutoff must be provided for absolute method")
        cutoff = absolute_cutoff
        good = df[df[affinity_col] <= absolute_cutoff]

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

    mapping = {}
    for r in results:
        if "symbol" in r and "query" in r:
            mapping[r["query"]] = r["symbol"]

    return mapping


def run_enrichment(protein_list, outdir):
    outdir.mkdir(parents=True, exist_ok=True)

    enr = gp.enrichr(
        gene_list=protein_list,
        gene_sets=[
            "GO_Biological_Process_2021",
            "GO_Molecular_Function_2021",
            "KEGG_2021_Human"
        ],
        organism="homo sapiens",
        outdir=str(outdir),
        cutoff=0.25,   # more permissive than default 0.05
        no_plot=True   # avoids crashes if no significant terms
    )

    return enr


def plot_top_enrichment(results, outdir, top_n=15):
    if results is None or results.empty:
        print("No enrichment results to plot.")
        return

    # Sort by adjusted p-value (more significant first)
    results_sorted = results.sort_values("Adjusted P-value").head(top_n)

    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=results_sorted,
        y="Term",
        x="Combined Score",
        palette="viridis"
    )

    plt.title("Top Enriched Pathways")
    plt.xlabel("Combined Score")
    plt.ylabel("")

    plt.tight_layout()
    plt.savefig(outdir / "top_enrichment_barplot.png")
    plt.close()

    print(f"Saved barplot to {outdir / 'top_enrichment_barplot.png'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--affinity_col", default="micromolar_affinity_pred_value")

    parser.add_argument("--method", choices=["percentile", "absolute"], default="percentile")
    parser.add_argument("--percentile", type=float, default=0.1)
    parser.add_argument("--absolute_cutoff", type=float, default=None)

    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.csv)

    # Select good binders
    good_df, cutoff = get_good_binders(
        df,
        affinity_col=args.affinity_col,
        method=args.method,
        value=args.percentile,
        absolute_cutoff=args.absolute_cutoff
    )

    print(f"Cutoff used: {cutoff}")
    print(f"Number of good binders: {len(good_df)}")

    # Map UniProt IDs → gene symbols
    accessions = good_df["protein"].dropna().unique().tolist()
    print(f"Mapping {len(accessions)} accessions to gene symbols...")

    mapping = map_to_gene_symbols(accessions)

    good_df["gene_symbol"] = good_df["protein"].map(mapping)

    # Drop unmapped
    gene_list = good_df["gene_symbol"].dropna().unique().tolist()

    print(f"Mapped to {len(gene_list)} gene symbols")

    if len(gene_list) == 0:
        print("No valid gene symbols found. Exiting.")
        return

    # Run enrichment
    outdir = Path("enrichment_analysis")
    print("Running enrichment...")

    enr = run_enrichment(gene_list, outdir)

    # Results
    results = enr.results

    if results is None or results.empty:
        print("No enrichment results found.")
    else:
        print("\nTop enrichment results:")
        print(results.head(10))

        results.to_csv(outdir / "enrichment_results.csv", index=False)
        print(f"\nSaved results to {outdir / 'enrichment_results.csv'}")

        plot_top_enrichment(results, outdir, top_n=20)

if __name__ == "__main__":
    main()