#!/usr/bin/env bash

ENV_FILE="capstone_path_env.sh"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Environment file not found: $ENV_FILE"
    exit 1
fi

. "$ENV_FILE"

echo "SOURCE_DIR=$SOURCE_DIR"

### TA note:
# This script would ordinarily process job submissions to
# the HPC to generate predictions. In this case, a dry run
# is performed to illustrate the process. The requisite data
# is included in the submitted folder on Learning Suite.

bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/random_plus_paul.csv" \
    --ligand_csv "$SOURCE_DIR/paul_metabolites.csv" \
    --job_name "random_plus_paul_metabolites" \
    --dry-run

bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/random_plus_paul.csv" \
    --ligand_csv "$SOURCE_DIR/c16_dihydroceramide.csv" \
    --job_name "random_plus_paul_c16dihydro" \
    --dry-run

bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/human_pisa_proteins.csv" \
    --ligand_csv "$SOURCE_DIR/c16_dihydroceramide.csv" \
    --job_name "pisa_c16dihydro" \
    --dry-run

bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/random_plus_paul.csv" \
    --ligand_csv "$SOURCE_DIR/c16_ceramide.csv" \
    --job_name "random_plus_paul_c16" \
    --dry-run

bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/human_pisa_proteins.csv" \
    --ligand_csv "$SOURCE_DIR/c16_ceramide.csv" \
    --job_name "pisa_c16_human" \
    --dry-run

# Local testing: leave control steps off
# python scripts/prep_control_data.py
# bash slurm_scripts/submit_dynamic_array.sh "control_tests"

echo "Finished generating all data necessary for figures."