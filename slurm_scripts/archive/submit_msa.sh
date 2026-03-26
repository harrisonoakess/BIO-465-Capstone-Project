#!/bin/bash
# submit_msa_safe.sh
# Safely submit all batches without hitting QOSMaxSubmitJobPerUserLimit

TOTAL_FILES=20416
BATCH_SIZE=1000
SCRIPT="run_msa.sh"

# Safe number of batches allowed in the queue
SAFE_LIMIT=1   # Set to 1 if unsure; adjust if CHPC tells you more

OFFSET=0

while [ $OFFSET -lt $TOTAL_FILES ]; do
    while true; do
        # Count current jobs in the partition for your user
        NUM_JOBS=$(squeue -u $USER -p kingspeak | wc -l)
        NUM_JOBS=$((NUM_JOBS - 1))  # subtract header line

        if [ "$NUM_JOBS" -lt "$SAFE_LIMIT" ]; then
            break
        fi

        echo "Max jobs reached ($NUM_JOBS). Waiting 60 seconds..."
        sleep 60
    done

    echo "Submitting batch with OFFSET=$OFFSET"
    sbatch --export=OFFSET=$OFFSET "$SCRIPT"

    OFFSET=$((OFFSET + BATCH_SIZE))
done

echo "All batches submitted (or in progress)."