import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import gseapy as gp
from mygene import MyGeneInfo
from pathlib import Path


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

def run_gsea_ranked(df, affinity_col, outdir, gene_sets, permutation_num=100):
    """
    Perform GSEA preranked analysis on all proteins.
    """
    outdir.mkdir(parents=True, exist_ok=True)

    # Convert binding affinities to scores: higher = stronger
    # Using -log10 so smaller micromolar = higher score
    df['affinity_score'] = -df[affinity_col].apply(lambda x: pd.to_numeric(x, errors='coerce')).replace(0, 1e-9).apply(lambda x: np.log10(x))
    df = df.dropna(subset=['affinity_score'])

    # Create prerank file
    rnk_file = outdir / "ranked_genes.rnk"
    df[['gene_symbol', 'affinity_score']].sort_values('affinity_score', ascending=False)\
        .to_csv(rnk_file, sep="\t", index=False, header=False)

    # Run GSEA preranked
    pre_res = gp.prerank(
        rnk=str(rnk_file),
        gene_sets=gene_sets,
        organism="Human",
        outdir=str(outdir),
        permutation_num=permutation_num,
        min_size=5,
        max_size=500,
        seed=42
    )
    return pre_res

def plot_gsea_top_enrichment(results_df, outdir, top_n=15, x_col="NES"):
    """
    Plot top enriched pathways from GSEA-ranked results.

    Parameters:
    - results_df: GSEA results dataframe (pre_res.res2d)
    - outdir: folder to save plot
    - top_n: number of top pathways to show
    - x_col: which metric to plot; options: "NES" or "-log10(FDR)"
    """

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if results_df.empty:
        print("No GSEA results to plot.")
        return

    # Compute -log10(FDR) if requested
    if x_col.lower() in ["-log10(fdr)", "neg_log10_fdr"]:
        results_df["neg_log10_fdr"] = -np.log10(results_df["fdr"])
        plot_col = "neg_log10_fdr"
        xlabel = "-log10(FDR)"
    elif x_col.upper() == "NES":
        plot_col = "NES"
        xlabel = "Normalized Enrichment Score"
    else:
        raise ValueError("x_col must be 'NES' or '-log10(FDR)'")

    # Sort by metric
    results_sorted = results_df.sort_values(plot_col, ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=results_sorted,
        y="Term",
        x=plot_col,
        palette="viridis"
    )

    # Optional threshold line for FDR
    if plot_col == "neg_log10_fdr":
        plt.axvline(x=-np.log10(0.05), color='red', linestyle='--', linewidth=1)
        plt.text(-np.log10(0.05)+0.05, plt.ylim()[1]*0.95, "FDR = 0.05", color='red', fontsize=10)

    plt.xlabel(xlabel)
    plt.ylabel("")
    plt.title(f"Top {top_n} GSEA-ranked pathways")
    plt.tight_layout()
    plt.savefig(outdir / f"gsea_top_{top_n}_barplot_{plot_col}.png")
    plt.close()
    print(f"Saved GSEA barplot to {outdir / f'gsea_top_{top_n}_barplot_{plot_col}.png'}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV with predicted affinities")
    parser.add_argument("--affinity_col", default="neg_log_molar_affinity_pred_value")
    parser.add_argument("--outdir", default="../gsea_ranked_results")
    parser.add_argument("--gene_sets", nargs="+", default=[
        "GO_Biological_Process_2021",
        "GO_Molecular_Function_2021",
        "KEGG_2021_Human"
    ])
    parser.add_argument("--permutation_num", type=int, default=100)
    args = parser.parse_args()

    # Load CSV
    df = pd.read_csv(args.csv)
    accessions = df["protein"].dropna().unique().tolist()
    print(f"Mapping {len(accessions)} accessions to gene symbols...")
    mapping = map_to_gene_symbols(accessions)
    df["gene_symbol"] = df["protein"].map(mapping)
    df = df.dropna(subset=['gene_symbol'])
    print(f"{len(df)} proteins mapped to gene symbols.")

    # Prepare output folder
    csv_name = Path(args.csv).stem
    outdir = Path(args.outdir) / csv_name
    outdir.mkdir(parents=True, exist_ok=True)

    # Run GSEA preranked analysis
    print("Running GSEA-ranked analysis...")
    pre_res = run_gsea_ranked(df, args.affinity_col, outdir, args.gene_sets, args.permutation_num)

    print("COLUMNS:")
    print(pre_res.res2d.columns)

    # Save results
    # find FDR-like column
    fdr_col = [c for c in pre_res.res2d.columns if 'fdr' in c.lower() or 'q-val' in c.lower()]
    if not fdr_col:
        raise ValueError("No FDR/q-value column found in GSEA results")
    fdr_col = fdr_col[0]

    gsea_results_sorted = pre_res.res2d.sort_values(fdr_col)
    gsea_results_sorted.to_csv(outdir / "gsea_ranked_results.csv", index=False)
    print(f"GSEA-ranked analysis complete. Results saved to {outdir / 'gsea_ranked_results.csv'}")

if __name__ == "__main__":
    main()