#!/bin/bash
#SBATCH --job-name=msa_array
#SBATCH --output=../logs/msa_%A_%a.log
#SBATCH --error=../logs/msa_%A_%a.log
#SBATCH --time=08:00:00
#SBATCH --partition=notchpeak-shared-short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --array=0-999 # Number of sequence chunks - 1

module purge
module load colabfold

# Path to chunked FASTAs
CHUNK_DIR="../prep_files/proteome_chunks"
FASTA_CHUNKS=($CHUNK_DIR/*.fasta)

# Map the SLURM_ARRAY_TASK_ID to the correct FASTA chunk
FASTA_FILE=${FASTA_CHUNKS[$SLURM_ARRAY_TASK_ID]}

# Output directory for each sequence
OUTPUT_DIR="../outputs/msa/$(basename $FASTA_FILE .fasta)"

# Check if MSA has already been generated (for idempotency)
if [ -f "$OUTPUT_DIR/msa.a3m" ]; then 
    echo "MSA already exists for $FASTA_FILE, skipping..."
    exit 0
fi

mkdir -p $OUTPUT_DIR

# Run MSA only using CHPC's local server
echo "Generating MSA for $FASTA_FILE ..."
colabfold_batch \
    --host-url=http://colabfold01.int.chpc.utah.edu:8088 \
    --msa-only \
    $FASTA_FILE \
    $OUTPUT_DIR 