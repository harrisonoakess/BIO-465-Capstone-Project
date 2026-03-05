#!/bin/bash
#SBATCH --job-name=boltz_proteome
#SBATCH --time=04:00:00
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mail-user=aw998@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL

# Define scratch project root
PROJECT_ROOT="/scratch/rai/vast1/stewartp"
SCRIPT_DIR="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts"
YAML_DIR="/scratch/rai/vast1/stewartp/yamls"

# Create log directories
mkdir -p "$PROJECT_ROOT/logs/array" "$PROJECT_ROOT/logs/runtime"


# Generate an array of yaml files
YAML_ARRAY=( "$YAML_DIR"/*.yaml )
NUM_YAML=${#YAML_ARRAY[@]}

echo "Found $NUM_YAML YAML files in $YAML_DIR"

# Submit array job, limiting concurrency to 50 GPUs at a time

sbatch \
    --array=0-$((NUM_YAML-1))%50 \
    --export=ALL,PROJECT_ROOT="$PROJECT_ROOT",YAML_DIR="$YAML_DIR" \
    "$SCRIPT_DIR/rai_array.sh"