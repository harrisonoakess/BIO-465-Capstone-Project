#!/bin/bash
#SBATCH --job-name=chunk_proteome
#SBATCH --output=../logs/chunk_proteome_%j.log
#SBATCH --error=../logs/chunk_proteome_%j.log
#SBATCH --time=00:10:00
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn-short
#SBATCH --account=rai
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -euo pipefail 

# Load Python module
module purge
module load python

PROTEOME_FASTA="../inputs/proteins/proteome.fasta"
OUT_DIR="/scratch/rai/vast1/stewartp/proteome_chunks"

mkdir -p ../logs
mkdir -p $OUT_DIR

# Run the Python script
python ../scripts/chunk_proteome.py \
    --fasta_file $PROTEOME_FASTA    \
    --out_dir $OUT_DIR

