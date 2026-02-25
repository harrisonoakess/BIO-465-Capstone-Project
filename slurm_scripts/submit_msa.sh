#!/bin/bash
TOTAL_FILES=20416
BATCH_SIZE=1000
SCRIPT="run_msa.sh"

OFFSET=0
MAX_SUBMIT=50  # set to your Kingspeak MaxSubmitJobs limit

while [ $OFFSET -lt $TOTAL_FILES ]; do
    # Wait if too many jobs pending
    while [ $(squeue -u $USER | wc -l) -ge $MAX_SUBMIT ]; do
        echo "Reached MaxSubmit ($MAX_SUBMIT). Waiting 1 minute..."
        sleep 60
    done

    echo "Submitting batch with OFFSET=$OFFSET"
    sbatch --export=OFFSET=$OFFSET "$SCRIPT"
    OFFSET=$((OFFSET + BATCH_SIZE))
done