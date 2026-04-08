#!/bin/bash

# This script creates CSVs to organize the Boltz outputs
# and creates a few key figures from the data

# Load environment variables - MAKE SURE YOU CHANGED YOUR LOCAL VARIABLES
ENV_FILE="capstone_path_env.sh"
if [ -f "$ENV_FILE" ]; then
    . "$ENV_FILE"
fi

mkdir -p "$PLOT_DIR"
echo "Project root is: $PROJECT_ROOT"
echo "Plots will be saved to: $PLOT_DIR"

### NOTE: TAs will not run this step!!! It is commented out. 
# CSV files will be given. This script goes through the Boltz
# predictions and consolidates the predictions into CSV files
# for convenience.

# Convert Boltz outputs to CSV -- processes all boltz outputs by default
# python scripts/output_parsing_to_csv.py --process_all --verbose
echo "Step 5 complete: CSV files created."

### Produce boxplots
# C16 Boxplot

C16_proteins_of_interest="$SOURCE_DIR/human_pisa_proteins.csv"
C16_all_proteins="$SOURCE_DIR/2000_random_proteins.csv"
C16_processed_data_1="$PROCESSED_DIR/confidence_predictions_pisa_c16_human.csv"
C16_processed_data_2="$PROCESSED_DIR/confidence_predictions_random_plus_paul_c16.csv"
C16_boxplot_script="$SCRIPT_DIR/create_figs/c16_boxplot.py"

echo "Creating C16 boxplot..."

python "$C16_boxplot_script" --proteins_of_interest_csv "$C16_proteins_of_interest" \
    --all_proteins_csv "$C16_all_proteins" \
    --processed_csv "$C16_processed_data_1" "$C16_processed_data_2"

# C16 dihydro boxplot

C16_dihydro_proteins_of_interest="$SOURCE_DIR/human_pisa_proteins.csv"
C16_dihydro_all_proteins="$SOURCE_DIR/2000_random_proteins.csv"
C16_dihydro_processed_data_1="$PROCESSED_DIR/confidence_predictions_pisa_c16dihydro.csv"
C16_dihydro_processed_data_2="$PROCESSED_DIR/confidence_predictions_random_plus_paul_c16dihydro.csv"
C16_dihydro_boxplot_script="$SCRIPT_DIR/create_figs/c16_dihydro_boxplot.py"

echo "Creating C16 dihydro boxplot..."

python "$C16_dihydro_boxplot_script" --proteins_of_interest_csv "$C16_dihydro_proteins_of_interest" \
    --all_proteins_csv "$C16_dihydro_all_proteins" \
    --processed_csv "$C16_dihydro_processed_data_1" "$C16_dihydro_processed_data_2"

# GlcNAc-ol boxplot

GlcNAc_ol_proteins_of_interest="$SOURCE_DIR/paul_proteins_2.csv"
GlcNAc_ol_all_proteins="$SOURCE_DIR/2000_random_proteins.csv"
GlcNAc_ol_processed_data_1="$PROCESSED_DIR/confidence_predictions_interest_proteins_paul_metabolites.csv"
GlcNAc_ol_processed_data_2="$PROCESSED_DIR/confidence_predictions_random_plus_paul_metabolites.csv"
GlcNAc_ol_boxplot_script="$SCRIPT_DIR/create_figs/GlcNAc-ol_boxplot.py"

echo "Creating GlcNAc-ol boxplot..."

python "$GlcNAc_ol_boxplot_script" --proteins_of_interest_csv "$GlcNAc_ol_proteins_of_interest" \
    --all_proteins_csv "$GlcNAc_ol_all_proteins" \
    --processed_csv "$GlcNAc_ol_processed_data_1" "$GlcNAc_ol_processed_data_2"

### Heat scatterplot of control data

control_analysis_output_folder="control_tests"
control_analysis_ref_file="control_proteins.csv"
control_analysis_script="$SCRIPT_DIR/create_figs/control_data_analysis.py"

echo "Creating heat scatterplot for control data..."

python "$control_analysis_script" --output_folder "$control_analysis_output_folder" \
    --ref_file "$control_analysis_ref_file"

### Heat scatterplot of ceramides

ceramide_analysis_csv_1="confidence_predictions_random_plus_paul_c16.csv"
ceramide_analysis_csv_2="confidence_predictions_random_plus_paul_c16dihydro.csv"
ligand_name_1="c16"
ligand_name_2="c16_dihydro"
ceramide_analysis_script="$SCRIPT_DIR/create_figs/heatscatter_plot.py"

echo "Creating heat scatterplot for ceramides..."

python "$ceramide_analysis_script" \
    --csvs "$ceramide_analysis_csv_1" "$ceramide_analysis_csv_2" \
    --ligand_names "$ligand_name_1" "$ligand_name_2"

# Enrichment plots
echo "Running enrichment analysis on $ENRICH_CSV..."

ENRICH_CSV="$PROCESSED_DIR/confidence_predictions_random_plus_paul_metabolites.csv"
ENRICH_SCRIPT="$SCRIPT_DIR/gseapy_ORA_analysis.py"
ENRICH_OUTDIR="$PLOT_DIR/enrichment_analysis"

echo "Running enrichment analysis on $ENRICH_CSV..."
echo "Processing CSV: $ENRICH_CSV"

echo "Running enrichment for all proteins..."
python "$ENRICH_SCRIPT" --csv "$ENRICH_CSV" --outdir "$ENRICH_OUTDIR"

echo "Running enrichment by ligand..."
python "$ENRICH_SCRIPT" --csv "$ENRICH_CSV" --by_ligand --outdir "$ENRICH_OUTDIR"

echo "Finished processing $ENRICH_CSV"

echo "Step 6 complete: Analysis and figure generation done."
