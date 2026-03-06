#!/bin/bash
#SBATCH --job-name=msa_per_protein
#SBATCH --output=/scratch/rai/vast1/stewartp/logs/msa_%A_%a.log
#SBATCH --error=/scratch/rai/vast1/stewartp/logs/msa_%A_%a.log
#SBATCH --time=08:00:00
#SBATCH --partition=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --array=0-999   # (can be overridden by sbatch --array=...)
#SBATCH --qos=rai-gpu-grn
#SBATCH --mail-user=hoakes@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL

set -euo pipefail

module --force purge
module load colabfold/1.5.5-0525

FASTA_DIR="/scratch/rai/vast1/stewartp/protein_fasta_files/proteome"
MSA_BASE="/scratch/rai/vast1/stewartp/msa_per_protein/proteome"

mkdir -p "$MSA_BASE"
mkdir -p "/scratch/rai/vast1/stewartp/logs"

mapfile -t FASTAS < <(ls -1 "$FASTA_DIR"/*.fasta | sort)

FASTA="${FASTAS[$SLURM_ARRAY_TASK_ID]:-}"
if [ -z "$FASTA" ]; then
  echo "No FASTA for index $SLURM_ARRAY_TASK_ID"
  exit 0
fi

NAME="$(basename "$FASTA" .fasta)"
OUTDIR="$MSA_BASE/$NAME"
mkdir -p "$OUTDIR"

if [ -f "$OUTDIR/msa.a3m" ]; then
  echo "MSA exists: $OUTDIR/msa.a3m"
  exit 0
fi

colabfold_batch \
  --host-url=http://colabfold01.int.chpc.utah.edu:8088 \
  --msa-only \
  "$FASTA" \
  "$OUTDIR"

# Normalize name to msa.a3m if needed
if [ ! -f "$OUTDIR/msa.a3m" ]; then
  CANDIDATE="$(ls -1 "$OUTDIR"/*.a3m 2>/dev/null | head -n 1 || true)"
  if [ -n "$CANDIDATE" ]; then
    ln -sf "$CANDIDATE" "$OUTDIR/msa.a3m"
  fi
fi

echo "Done: $OUTDIR"