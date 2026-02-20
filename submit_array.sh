#!/bin/bash
# Usage:
# bash submit_array.sh <input_yaml_directory>

set -e

if [ -z "$1" ]; then 
    echo "Usage: bash submit_array.sh <input_yaml_directory>"
    exit 1
fi

INPUT_DIR="$1"

if [ ! -d "$INPUT_DIR" ]; then 
    echo "Error: Directory $INPUT_DIR does not exist"
    exit 1 
fi

PROJECT_ROOT=$(pwd)
YAML_LIST="${PROJECT_ROOT}/yaml_list.txt"

echo "Creating YAML list from: $INPUT_DIR"
find "$INPUT_DIR" -type f -name "*.yaml" | sort > "$YAML_LIST"

TOTAL=$(wc -l < "$YAML_LIST")

if [ "$TOTAL" -eq 0 ]; then
    echo "No YAML files found."
    exit 1
fi

echo "Found $TOTAL YAML files."

# Max array size allowed by cluster is 1000
MAX_ARRAY_SIZE=10
CONCURRENT=2  # corresponds to %50 in --array
JOB_SCRIPT="${PROJECT_ROOT}/slurm_scripts/notchpeak_job_array.sh"

START=0

while [ $START -lt $TOTAL ]; do
    END=$((START + MAX_ARRAY_SIZE - 1))
    if [ $END -ge $((TOTAL - 1)) ]; then
        END=$((TOTAL - 1))
    fi

    echo "Submitting array ${START}-${END}%$CONCURRENT ..."
    sbatch \
        --array=${START}-${END}%$CONCURRENT \
        --export=ALL,YAML_LIST="$YAML_LIST",PROJECT_ROOT="$PROJECT_ROOT" \
        "$JOB_SCRIPT"

    START=$((END + 1))
done
