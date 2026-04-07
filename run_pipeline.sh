#!/usr/bin/env bash

set -euo pipefail
module load python

# This script produces YAML files to be run by Boltz-2
# and submits the jobs to the University of Utah HPC.

# Run the pipeline:
# bash run_pipeline.sh --protein_csv <protein file> --ligand_csv <ligand file> [--use_proteome] [--dry-run]

# --use_proteome: download proteome if no protein file is given
# --dry-run: run without submitting jobs

echo "Starting pipeline..."

# Load environment variables - MAKE SURE YOU CHANGED THEM TO YOUR LOCAL VARIABLES in capstone_path_env.sh
ENV_FILE="capstone_path_env.sh"
if [ -f "$ENV_FILE" ]; then
    . "$ENV_FILE"
fi

SMILES_TXT=""
PROTEIN_CSV=""
LIGAND_CSV=""
USE_PROTEOME=0
JOB_NAME=""

DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --protein_csv)
            PROTEIN_CSV="$2"
            shift 2
            ;;
        --ligand_csv)
            LIGAND_CSV="$2"
            shift 2
            ;;
        --job_name)
            JOB_NAME="$2"
            shift 2
            ;;
        --proteome)
            USE_PROTEOME=1
            shift
            ;;
        --smiles_txt)
            SMILES_TXT="$2"
            shift 2
            ;;
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

# Validate input arguments
if [[ "$USE_PROTEOME" -eq 1 ]]; then
    echo "Running in proteome mode (auto download + convert)."
else
    if [[ -z "$PROTEIN_CSV" || -z "$LIGAND_CSV" ]]; then
        echo "ERROR: You must provide --protein_csv and --ligand_csv OR use --proteome"
        exit 1
    fi
    echo "Running in manual CSV mode."
fi

# Ensure directories exist
mkdir -p "$YAML_DIR"

# Step 0: Check ligand CSV
echo "Checking ligand CSV..."
if [[ -n "$LIGAND_CSV" ]]; then
    if [[ ! -f "$LIGAND_CSV" ]]; then
        echo "ERROR: Ligand CSV not found at $LIGAND_CSV"
        exit 1
    fi
    echo "Using ligand CSV: $LIGAND_CSV"
else
    if ! ls "$LIGAND_DIR"/*.csv >/dev/null 2>&1; then
        echo "ERROR: No CSV file found in $LIGAND_DIR"
        exit 1
    fi
    echo "Using ligand CSVs in directory: $LIGAND_DIR"
fi
echo "Ligand CSV found."

if [[ "$USE_PROTEOME" -eq 1 ]]; then
    echo "Checking protein files..."

    # Step 1: Download proteome
    if [ ! -f "$FASTA_FILE" ]; then
        echo "Proteome FASTA missing. Downloading..."
        python scripts/download_proteome_fasta.py \
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

    PROTEIN_CSV="$CSV_FILE"
fi

# Step 3: Generate YAMLs
echo "Generating YAML files..."

GENERATE_ARGS=(
    --proteome_csv "$PROTEIN_CSV"
    --ceramide_csv "$LIGAND_CSV"
    --msa_base_dir "$MSA_BASE_DIR"
    --out_base_dir "$YAML_DIR"
)

if [[ -n "${SMILES_TXT:-}" ]]; then
    GENERATE_ARGS+=(--smiles_txt "$SMILES_TXT")
fi

python scripts/generate_yaml.py "${GENERATE_ARGS[@]}"

echo "Step 3 complete. All YAMLs generated."

# Step 4: Submit Boltz jobs
if [ "$DRY_RUN" -eq 1 ]; then
    echo "[DRY RUN] Skipping Boltz job submission."
    echo "[DRY RUN] Would have submitted jobs using submit_dynamic_array.sh for $JOB_NAME"
else
    echo "Submitting Boltz jobs..."
    bash "$PROJECT_ROOT/slurm_scripts/submit_dynamic_array.sh" "$JOB_NAME"
    echo "Boltz jobs submitted for $JOB_NAME."
fi
echo "Step 4 complete. Boltz jobs submitted."