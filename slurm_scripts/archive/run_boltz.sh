#!/bin/bash
set -euo pipefail

module purge
module load boltz2

YAML_FILE="$1"
OUT_DIR="$2"
THREADS="$3"

mkdir -p "$OUT_DIR"

echo "----------------------------------------"
echo "Running Boltz on $(hostname)"
echo "YAML: $YAML_FILE"
echo "Output: $OUT_DIR"
echo "----------------------------------------"

boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold01.int.chpc.utah.edu:8088 \
    --num_workers "$THREADS" \
    --out_dir "$OUT_DIR"

echo "Finished $YAML_FILE"