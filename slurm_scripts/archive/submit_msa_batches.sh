#!/bin/bash
set -u

TOTAL_FILES=20416
BATCH_SIZE=1000
TASK_LIMIT=950
SCRIPT="run_msa_per_protein.sh"
PARTITION="rai-gpu-grn"
JOBNAME="msa_per_protein"

FASTA_DIR="/scratch/rai/vast1/stewartp/protein_fasta_files/proteome"
MSA_BASE="/scratch/rai/vast1/stewartp/msa_per_protein/proteome"

mapfile -t FASTAS < <(ls -1 "$FASTA_DIR"/*.fasta | sort)

OFFSET=0
while [ $OFFSET -lt $TOTAL_FILES ]; do
  COUNT=$BATCH_SIZE
  if [ $((OFFSET + COUNT)) -gt $TOTAL_FILES ]; then
    COUNT=$((TOTAL_FILES - OFFSET))
  fi

  START=$OFFSET
  END_GLOBAL=$((OFFSET + COUNT - 1))

  done_count=0
  for ((i=START; i<=END_GLOBAL; i++)); do
    fasta="${FASTAS[$i]:-}"
    [ -z "$fasta" ] && continue
    name="$(basename "$fasta" .fasta)"
    if [ -f "$MSA_BASE/$name/msa.a3m" ]; then
      done_count=$((done_count + 1))
    fi
  done

  if [ "$done_count" -eq "$COUNT" ]; then
    echo "Batch $START-$END_GLOBAL already complete ($done_count/$COUNT). Skipping submit."
    OFFSET=$((OFFSET + BATCH_SIZE))
    continue
  else
    echo "Batch $START-$END_GLOBAL incomplete ($done_count/$COUNT). Submitting..."
  fi

  while true; do
    TASKS=$(squeue -u "$USER" -p "$PARTITION" -n "$JOBNAME" -h -r | wc -l)
    if [ "$TASKS" -le "$TASK_LIMIT" ]; then
      break
    fi
    echo "Too many tasks submitted (tasks=$TASKS). Sleeping 60s..."
    sleep 60
  done

  END_LOCAL=$((COUNT - 1))
  while true; do
    OUT=$(sbatch --export=ALL,OFFSET=$START --array=0-$END_LOCAL "$SCRIPT" 2>&1)
    RC=$?
    if [ $RC -eq 0 ]; then
      echo "$OUT"
      break
    fi
    echo "sbatch failed: $OUT"
    echo "Sleeping 60s then retrying..."
    sleep 60
  done

  OFFSET=$((OFFSET + BATCH_SIZE))
done

echo "All batches handled."