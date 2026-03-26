#!/bin/bash
#SBATCH --job-name=boltz_worker
#SBATCH --time=04:00:00
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mail-user=mander19@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h200:1
#SBATCH --mem=32G

set -euo pipefail

# module purge
# module load boltz2

# Paths
PROJECT_ROOT=${PROJECT_ROOT:-"/scratch/rai/vast1/stewartp"}
# SCRIPT_DIR=${SCRIPT_DIR:-"$PROJECT_ROOT/slurm_scripts"}
OUTPUT_DIR="$OUTPUT_DIR"
YAML_LIST=${YAML_LIST:-"$PROJECT_ROOT/yaml_list.txt"}
TOTAL_YAMLS=$(wc -l < "$YAML_LIST")
echo "Yaml list path: $YAML_LIST"

# Pick YAML for this task
YAML_FILE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$YAML_LIST")
JOB_NAME=${YAML_FILE:-"boltz_job"}

echo "----------------------------------------"
echo "Running task $SLURM_ARRAY_TASK_ID on $(hostname)"
echo "Processing YAML: $YAML_FILE"
echo "Progress: $((SLURM_ARRAY_TASK_ID + 1)) / $TOTAL_YAMLS"
echo "----------------------------------------"

# Run Boltz
boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold01.int.chpc.utah.edu:8088 \
    --num_workers 4 \
    --out_dir "$OUTPUT_DIR" \
    # --override

echo ""
echo "----------------------------------------"
echo "Task $SLURM_ARRAY_TASK_ID completed YAML: $YAML_FILE"
echo "----------------------------------------"