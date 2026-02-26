#!/bin/bash
#SBATCH --job-name=msa_array
#SBATCH --output=../logs/msa_%A_%a.log
#SBATCH --error=../logs/msa_%A_%a.log
#SBATCH --time=08:00:00
#SBATCH --partition=kingspeak
#SBATCH --account=stewartp
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --array=0-999   # 1000 tasks per batch

OFFSET=${OFFSET:-0}    # Passed by submit_msa.sh

module purge
module load colabfold/1.5.5-0525

CHUNK_DIR="../prep_files/proteome_chunks"
OUTPUT_BASE="../outputs/msa"

# Load all FASTA files
mapfile -t FASTA_CHUNKS < <(ls -1 "$CHUNK_DIR"/*.fasta)

# Compute global index
GLOBAL_INDEX=$((SLURM_ARRAY_TASK_ID + OFFSET))
FASTA_FILE="${FASTA_CHUNKS[$GLOBAL_INDEX]}"

if [ -z "$FASTA_FILE" ]; then
    echo "No FASTA file for global index $GLOBAL_INDEX, skipping..."
    exit 0
fi

OUTPUT_DIR="$OUTPUT_BASE/$(basename $FASTA_FILE .fasta)"
mkdir -p "$OUTPUT_DIR"

# Skip if MSA already exists
if [ -f "$OUTPUT_DIR/msa.a3m" ]; then
    echo "MSA already exists for $FASTA_FILE, skipping..."
    exit 0
fi

echo "Generating MSA for $FASTA_FILE ..."
colabfold_batch \
    --host-url=http://colabfold01.int.chpc.utah.edu:8088 \
    --msa-only \
    "$FASTA_FILE" \
    "$OUTPUT_DIR"