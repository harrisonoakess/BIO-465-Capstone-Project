#!/usr/bin/env bash

# These are the combinations that you would run (and wait several days for the HPC to complete)
# before generating graphs from the boltz results

# Load environment variables - MAKE SURE YOU CHANGED THEM TO YOUR LOCAL VARIABLES in capstone_path_env.sh
ENV_FILE="capstone_path_env.sh"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Environment file not found: $ENV_FILE"
    exit 1
fi

. "$ENV_FILE"

echo "SOURCE_DIR=$SOURCE_DIR"

# Glcnacol vs. random and Aldo-keto-reductase data
bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/random_plus_pauls.csv" \
    --ligand_csv "$SOURCE_DIR/paul_metabolites.csv" \
    --job_name "random_plus_paul_metabolites" \
    --dry-run

# Ceramide data for C16 Dihydro vs. random
bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/random_plus_pauls.csv" \
    --ligand_csv "$SOURCE_DIR/c16_dihydroceramide.csv" \
    --job_name "random_plus_paul_c16dihydro" \
    --dry-run

# Ceramide data for C16 Dihydro vs. human PISA data
bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/human_pisa_proteins.csv" \
    --ligand_csv "$SOURCE_DIR/c16_dihydroceramide.csv" \
    --job_name  "pisa_c16dihydro" \
    --dry-run

# Ceramide data for C16 vs. random
bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/random_plus_paul.csv" \
    --ligand_csv "$SOURCE_DIR/c16_ceramide.csv" \
    --job_name "random_plus_pauls_c16" \
    --dry-run

# Ceramide data for C16 vs. human PISA data
bash run_pipeline.sh \
    --protein_csv "$SOURCE_DIR/human_pisa_proteins.csv" \
    --ligand_csv "$SOURCE_DIR/c16_ceramide.csv" \
    --job_name "pisa_c16_human" \
    --dry-run

# Control data - Since this dataset is not a combination of each possible protein-ligand pairing,
# the preprocessing was handled separately. 

# Create the control .yaml files (input for Boltz)
python scripts/prep_control_data.py 

# Run Boltz
bash slurm_scripts/submit_dynamic_array.sh "control_tests"

echo "Finished generating all data necessary for figures."
