#!/bin/bash
#SBATCH --job-name=boltz_array
#SBATCH --output=../logs/array/boltz_%A_%a.log
#SBATCH --error=../logs/array/boltz_%A_%a.log
#SBATCH --array=0-44
#SBATCH --time=02:00:00
#SBATCH --partition=notchpeak-gpu
#SBATCH --qos=notchpeak-gpu
#SBATCH --account=notchpeak-gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G

mkdir -p ../logs/array
mkdidr -p outputs

module purge
module load boltz2

# FIRST create a yaml_list.txt file
# find prep_files/boltz_ready/paul_tests/ -type f -name "*.yaml" | sort > test_yaml_list.txt
# Check its size:
# wc -l test_yaml_list.txt 
# Set (0-file length - 1) as the array size

YAML_LIST="../test_yaml_list.txt"

# Get the YAML file corresponding to the SLURM_ARRAY_TASK_ID
YAML_FILE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$YAML_LIST")

if [ -z "$YAML_FILE" ]; then 
    echo "No YAML file found for task $SLURM_ARRAY_TASK_ID"
    exit 1
fi 

echo "Running task ${SLURM_ARRAY_TASK_ID}"
echo "Processing file: $YAML_FILE"

echo "Start time: $(date)"

START=$(date +%s)

boltz predict "$YAML_FILE" \
    --use_msa_server \
    --num_workers 8 \
    --out_dir ../outputs \
    --override

END=$(date +%s)
RUNTIME=$((END-START))

echo "End time: $(date)"
echo "Elapsed time: ${RUNTIME} seconds"

# Append to CSV for summary
echo "${SLURM_ARRAY_TASK_ID},${YAML_FILE},${RUNTIME}" >> ../logs/array/runtime_summary.csv

# Run this in the terminal to run without hardcoding the array size
# N=$(wc -l < yaml_list.txt)
# sbatch --array=0-$(($N-1)) notchpeak_job_array.sh

# Max Array Size = 1000
# Submit in chunks like this:
# sbatch --array=0-999%50 notchpeak_job_array.sh
# sbatch --array=1000-1999%50 notchpeak_job_array.sh
# sbatch --array=2000-2999%50 notchpeak_job_array.sh
# sbatch --array=3000-3999%50 notchpeak_job_array.sh
# sbatch --array=4000-4999%50 notchpeak_job_array.sh
# sbatch --array=5000-5999%50 notchpeak_job_array.sh
# sbatch --array=6000-6999%50 notchpeak_job_array.sh
# sbatch --array=7000-7999%50 notchpeak_job_array.sh
# sbatch --array=8000-8999%50 notchpeak_job_array.sh
# sbatch --array=9000-9066%50 notchpeak_job_array.sh