#!/bin/bash
set -euo pipefail

TOTAL_FILES=20416
BATCH_SIZE=1000
SAFE_LIMIT=3
SCRIPT="run_msa_per_protein.sh"
PARTITION="rai-gpu-grn"

OFFSET=0
while [ $OFFSET -lt $TOTAL_FILES ]; do
  while true; do
    NUM_JOBS=$(squeue -u "$USER" -p "$PARTITION" | wc -l)
    NUM_JOBS=$((NUM_JOBS - 1))
    if [ "$NUM_JOBS" -lt "$SAFE_LIMIT" ]; then
      break
    fi
    echo "Max jobs reached ($NUM_JOBS). Sleeping 60s..."
    sleep 60
  done

  START=$OFFSET
  END=$((OFFSET + BATCH_SIZE - 1))
  if [ $END -ge $((TOTAL_FILES - 1)) ]; then
    END=$((TOTAL_FILES - 1))
  fi

  echo "Submitting array $START-$END"
  sbatch --array=$START-$END "$SCRIPT"

  OFFSET=$((OFFSET + BATCH_SIZE))
done

echo "All batches submitted (or in progress)."