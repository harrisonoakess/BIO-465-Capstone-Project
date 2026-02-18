#!/bin/bash
# Wrapper to auto-chunk Slurm array submissions for notchpeak-gpu
# *** Run with bash submit_array.sh 

# Max array size allowed by cluster
MAX_ARRAY_SIZE=1000

# Max concurrent tasks per chunk
CONCURRENT=50  # corresponds to %50 in --array

# Path to array job script
JOB_SCRIPT="slurm_scripts/notchpeak_job_array.sh"

# Path to your YAML list
YAML_LIST="test_yaml_list.txt"

# Total number of YAML files
TOTAL=$(wc -l < "$YAML_LIST")

START=0

while [ $START -lt $TOTAL ]; do
    END=$((START + MAX_ARRAY_SIZE - 1))
    if [ $END -ge $((TOTAL - 1)) ]; then
        END=$((TOTAL - 1))
    fi

    echo "Submitting array ${START}-${END}%$CONCURRENT ..."
    sbatch --array=${START}-${END}%$CONCURRENT "$JOB_SCRIPT"

    START=$((END + 1))
done
