#!/bin/bash
#SBATCH --job-name=boltz_worker
#SBATCH --time=08:00:00
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mail-user=aw998@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1

set -euo pipefail

# Paths
PROJECT_ROOT=${PROJECT_ROOT:-"/scratch/rai/vast1/stewartp"}
YAML_LIST=${YAML_LIST:-"$PROJECT_ROOT/yaml_list.txt"}
OUT_DIR="$PROJECT_ROOT/outputs/${SLURM_ARRAY_TASK_ID}"
mkdir -p "$OUT_DIR"

# Pick YAML for this task
YAML_FILE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$YAML_LIST")

echo "----------------------------------------"
echo "Running task $SLURM_ARRAY_TASK_ID on $(hostname)"
echo "Processing YAML: $YAML_FILE"
echo "Progress: $((SLURM_ARRAY_TASK_ID + 1)) / $TOTAL_YAMLS"
echo "----------------------------------------"

# Run Boltz
boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold01.int.chpc.utah.edu:8088 \
    --num_workers $SLURM_CPUS_PER_TASK \
    --out_dir "$OUT_DIR" \
    --override

echo "Task $SLURM_ARRAY_TASK_ID completed YAML: $YAML_FILE"
echo "----------------------------------------"