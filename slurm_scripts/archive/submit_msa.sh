#!/bin/bash
# submit_msa_safe.sh
# Safely submit all batches without hitting QOSMaxSubmitJobPerUserLimit

TOTAL_FILES=20416
BATCH_SIZE=1000
SCRIPT="run_msa.sh"

# Safe number of batches allowed in the queue
SAFE_LIMIT=1   # Set to 1 if unsure; adjust if CHPC tells you more

OFFSET=0

#!/bin/bash
# submit_msa_safe.sh
# Safely submit all batches without hitting the 1000-job limit

TOTAL_FILES=20416
BATCH_SIZE=500
SCRIPT="run_msa.sh"
MAX_JOBS=1000

OFFSET=0

while [ "$OFFSET" -lt "$TOTAL_FILES" ]; do
    while true; do
        NUM_JOBS=$(squeue -u "$USER" -h -p kingspeak | wc -l)

        # Only submit if there is room for the next batch
        if [ $((NUM_JOBS + BATCH_SIZE)) -le "$MAX_JOBS" ]; then
            break
        fi

        echo "Currently $NUM_JOBS jobs in queue. Waiting 60 seconds..."
        sleep 60
    done

    echo "Submitting batch with OFFSET=$OFFSET"
    sbatch --export=OFFSET="$OFFSET" "$SCRIPT"

    OFFSET=$((OFFSET + BATCH_SIZE))
done

echo "All batches submitted."