import os
from pathlib import Path
import pandas as pd

# Load your Excel file, skip first row if it contains merged group headers
df = pd.read_excel("../inputs/proteins/pisa_proteins.xlsx", header=1)

# The columns should now be like:
# hiPSC-CM ProteinID, hiPSC-CM GeneSymbol, NaN, HBMVEC ProteinID, HBMVEC GeneSymbol, etc.

# List of groups in order
groups = ["hiPSC-CM", "HBMVEC", "PTEC", "Ins1"]

rows = []

# Start index of the first ProteinID column
col_idx = 0

for group in groups:
    prot_col = df.columns[col_idx]
    gene_col = df.columns[col_idx + 1]
    
    temp = df[[prot_col, gene_col]].copy()
    temp = temp.dropna(subset=[prot_col, gene_col])  # drop empty rows
    
    temp.rename(columns={prot_col: 'protein', gene_col: 'gene_symbol'}, inplace=True)
    temp['group'] = group
    rows.append(temp)
    
    # Move to next group (skip one empty column if exists)
    col_idx += 3  # ProteinID + GeneSymbol + empty column

# Combine all groups
mapping_df = pd.concat(rows, ignore_index=True)

# Create output directory
outdir = Path("../enrichment_analysis/mapping")
outdir.mkdir(parents=True, exist_ok=True)

# Save CSV
output = outdir / "pisa_protein_group_mapping.csv"
mapping_df.to_csv(output, index=False)
print(f"Mapping CSV saved: {output}")