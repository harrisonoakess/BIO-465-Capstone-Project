#!/bin/bash
set -euo pipefail

FASTA_FILE="$1"
OUTPUT_DIR="$2"

module purge
module load colabfold/1.5.5-0525

mkdir -p "$OUTPUT_DIR"

# Skip if already exists
if [ -f "$OUTPUT_DIR/msa.a3m" ]; then
    echo "MSA already exists for $FASTA_FILE, skipping..."
    exit 0
fi

echo "Generating MSA for $FASTA_FILE"

colabfold_batch \
    --host-url=http://colabfold01.int.chpc.utah.edu:8088 \
    --msa-only \
    "$FASTA_FILE" \
    "$OUTPUT_DIR"