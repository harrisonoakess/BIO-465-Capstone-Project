#!/usr/bin/env bash

set -euo pipefail
module load python

# This script produces YAML files to be run by Boltz-2
# and submits the jobs to the University of Utah HPC.

echo "Starting pipeline..."

# Load environment variables - MAKE SURE YOU CHANGED THEM TO YOUR LOCAL VARIABLES
ENV_FILE="slurm_scripts/capstone_path_env.sh"
if [ -f "$ENV_FILE" ]; then
    . "$ENV_FILE"
fi

# FILL IN HERE: Choose which ligand CSV and protein CSV 
# you want to generate combinations for
PROTEIN_CSV=
LIGAND_CSV=

DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Ensure directories exist
mkdir -p "$PROTEIN_DIR" "$LIGAND_DIR" "$YAML_DIR"

# Step 0: Check ligand CSV
echo "Checking ligand files..."
if ! ls "$LIGAND_DIR"/*.csv >/dev/null 2>&1; then
    echo "ERROR: No CSV file found in $LIGAND_DIR"
    exit 1
fi
echo "Ligand CSV found."

# Step 1: Download proteome if missing
echo "Checking protein files..."
# Check if protein directory is empty
if [ ! -f "$FASTA_FILE" ]; then
    echo "Proteome FASTA missing. Downloading..."
    python scripts/download_proteome.py \
        --proteome_id UP000005640 \
        --output "$FASTA_FILE"
    echo "Proteome downloaded."
else
    echo "FASTA already exists. Skipping download."
fi
echo "Step 1 complete."

# Step 2: Convert FASTA to CSV
echo "Running FASTA → CSV conversion..."
if [ ! -f "$CSV_FILE" ]; then
    python scripts/proteome_fasta_to_csv.py \
        --input "$FASTA_FILE" \
        --output "$CSV_FILE"
    echo "CSV created at $CSV_FILE"
else
    echo "CSV already exists. Skipping conversion."
fi
echo "Step 2 complete."

# TO DO: Change generate_yaml.py to accept one ligand and one protein csv
# TO DO: Add cofactor argument that can read a .txt file and add the SMILES to the .yaml
# TO DO: Change output_yaml to output_dir and route to a directory of outputs

# Step 3: Generate YAMLs for each ligand
echo "Generating YAML files..."
for ligand_csv in "$LIGAND_DIR"/*.csv; do 
    while IFS=, read -r ligand_id ligand_type ligand_value; do 
        # Skip header row
        if [ "$ligand_id" == "ligand_id" ]; then
            continue
        fi

        # Remove extra whitespace / tabs
        ligand_id=$(echo "$ligand_id" | xargs)
        ligand_type=$(echo "$ligand_type" | xargs)
        ligand_value=$(echo "$ligand_value" | xargs)

        yaml_file="$YAML_DIR/${ligand_id}.yaml"

        if [ -f "$yaml_file" ]; then 
            echo "YAML $yaml_file already exists. Skipping."
            continue
        fi

        python scripts/generate_yaml.py \
            --fasta_file "$FASTA_FILE" \
            --ligand_id "$ligand_id" \
            --ligand_type "$ligand_type" \
            --ligand_value "$ligand_value" \
            --output_yaml "$yaml_file"

        echo "Created YAML: $yaml_file"
    done < "$ligand_csv"
done
echo "Step 3 complete. All YAMLs generated."

# Step 4: Submit Boltz jobs
if [ "$DRY_RUN" -eq 1 ]; then
    echo "[DRY RUN] Skipping Boltz job submission."
    echo "[DRY RUN] Would have submitted jobs using submit_dynamic_array.sh"
else
    echo "Submitting Boltz jobs..."
    JOB_NAME="boltz_run_$(date +%Y%m%d_%H%M%S)"
    bash "$PROJECT_ROOT/slurm_scripts/submit_dynamic_array.sh" "$JOB_NAME" 1
    echo "Boltz jobs submitted for $JOB_NAME."
fi
echo "Step 4 complete. Boltz jobs submitted."
