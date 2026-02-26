#!/bin/bash
#SBATCH --job-name=boltz_array
#SBATCH --output=logs/array/boltz_%A_%a.log
#SBATCH --error=logs/array/boltz_%A_%a.log
#SBATCH --time=00:30:00
#SBATCH --partition=notchpeak-gpu
#SBATCH --qos=notchpeak-gpu
#SBATCH --account=notchpeak-gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --requeue

set -e

if [ -z "$PROJECT_ROOT" ] || [ -z "$YAML_LIST" ]; then
    echo "Error: PROJECT_ROOT or YAML_LIST not set."
    echo "Submit this job using submit_array.sh"
    exit 1
fi

cd "$PROJECT_ROOT"
mkdir -p logs/array
mkdir -p outputs

RUNTIME_FILE="logs/array/runtime_summary.csv"

module --force purge
module load boltz2

echo "===== GPU CHECK ====="
nvidia-smi || {
    echo "nvidia-smi failed. Requeueing job..."
    scontrol requeue $SLURM_JOB_ID
    exit 1
}

# Verify CUDA is visible to PyTorch
python - <<EOF
import torch
if not torch.cuda.is_available():
    raise SystemExit("CUDA not available")
print("CUDA available:", torch.cuda.get_device_name(0))
EOF

if [ $? -ne 0 ]; then
    echo "CUDA not available to PyTorch. Requeuing..."
    scontrol requeue $SLURM_JOB_ID
    exit 1
fi

# Number of proteins to run in this job
INDEX=$((SLURM_ARRAY_TASK_ID + 1))
YAML_FILE=$(sed -n "${INDEX}p" "$YAML_LIST")

if [ -z "$YAML_FILE" ]; then 
    echo "No YAML file for index $INDEX"
    exit 0
fi

TOTAL=$(wc -l < "$YAML_LIST")

if [ $END -gt $TOTAL ]; then
    END=$TOTAL
fi

NODE=$(hostname)

YAML_FILE=$(sed -n "${i}p" "$YAML_LIST")
[ -z "$YAML_FILE" ] && break
    
START_TIME=$(date +%s)
START_DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo "Running task ${SLURM_ARRAY_TASK_ID} on $NODE"
echo "Processing file: $YAML_FILE"
echo "Start time: $START_DATE"

# Run Boltz
boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold01.int.chpc.utah.edu:8088 \
    --num_workers 8 \
    --out_dir outputs \
    --override

EXIT_CODE=$?

END_TIME=$(date +%s)
END_DATE=$(date +"%Y-%m-%d %H:%M:%S")
RUNTIME=$((END_TIME - START_TIME))

echo "End time: $END_DATE"
echo "Elapsed time: ${RUNTIME} seconds"

# Append safely to runtime CSV
(
    flock -x 200
    if [ ! -f "$RUNTIME_FILE" ]; then
        echo "task_id,yaml_file,node,start_time,end_time,runtime_seconds,exit_code" > "$RUNTIME_FILE"
    fi
    echo "${SLURM_ARRAY_TASK_ID},${YAML_FILE},${NODE},${START_DATE},${END_DATE},${RUNTIME},${EXIT_CODE}" >> "$RUNTIME_FILE"
) 200>logs/array/runtime_summary.lock

# Requeue if Boltz failed
if [ $EXIT_CODE -ne 0 ]; then
    echo "Boltz failed with exit code $EXIT_CODE. Requeuing..."
    scontrol requeue $SLURM_JOB_ID
    exit 1
fi


echo "===== JOB COMPLETE ====="