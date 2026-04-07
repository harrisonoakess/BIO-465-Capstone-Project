#!/bin/bash

# This script creates CSVs to organize the Boltz outputs
# and creates a few key figures from the data

# Load environment variables - MAKE SURE YOU CHANGED YOUR LOCAL VARIABLES
ENV_FILE="slurm_scripts/capstone_path_env.sh"
if [ -f "$ENV_FILE" ]; then
    . "$ENV_FILE"
fi

# Choose which CVS's to create plots for
ENRICH_CSV="$PROCESSED_DIR/confidence_predictions_random_plus_paul_metabolites.csv"
# BOXPLOT_CSV="$PROCESSED_DIR/"
# SCATTER_CSV=""
# CONTROL_CSV=""

echo "Project root is: $PROJECT_ROOT"
echo "Plots will be saved to: $PLOT_DIR"

# Convert Boltz outputs to CSV -- processes all boltz outputs by default
# NOTE: TAs will not run this step!!! It is commented out. CSV files will be given.
echo "Processing Boltz outputs into CSV..."
#python scripts/output_parsing_to_csv.py --verbose
echo "Step 5 complete: CSV files created."

# TO DO: Boxplot

# TO DO: Heat scatterplot of control data

# TO DO: Heat scatterplot of ceramides

# Enrichment plots
echo "Running enrichment analysis on $ENRICH_CSV..."

ENRICH_SCRIPT="$PROJECT_ROOT/gseapy_ORA_analysis.py"
ENRICH_OUTDIR="$PLOT_DIR/enrichment_analysis"
echo "Processing CSV: $ENRICH_CSV"
echo "Running enrichment for all proteins..."
python "$ENRICH_SCRIPT" --csv "$ENRICH_CSV" --by_ligand False --outdir "$ENRICH_OUTDIR"

echo "Running enrichment by ligand..."
python "$ENRICH_SCRIPT" --csv "$ENRICH_CSV" --by_ligand True --outdir "$ENRICH_OUTDIR"
echo "Finished processing $ENRICH_CSV"

echo "Step 6 complete: Enrichment analysis done."