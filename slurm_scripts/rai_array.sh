#!/bin/bash
set -euo pipefail

# Paths
PROJECT_ROOT=${PROJECT_ROOT:-"/scratch/rai/vast1/stewartp"}
YAML_DIR=${YAML_DIR:-"$PROJECT_ROOT/yamls"}
OUT_DIR="$PROJECT_ROOT/outputs/${SLURM_ARRAY_TASK_ID}"
mkdir -p "$OUT_DIR"

# Create an array of YAMLs for this job
YAML_ARRAY=( "$YAML_DIR"/*.yaml )

# Pick YAML for this task
INDEX=$SLURM_ARRAY_TASK_ID
YAML_FILE="${YAML_ARRAY[$INDEX]}"

echo "Running task $INDEX on $(hostname)"
echo "Processing YAML: $YAML_FILE"

# Run Boltz
boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold01.int.chpc.utah.edu:8088 \
    --num_workers $SLURM_CPUS_PER_TASK \
    --out_dir "$OUT_DIR" \
    --override