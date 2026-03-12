#!/bin/bash
#SBATCH --job-name=boltz_submit
#SBATCH --time=00:10:00
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mail-user=aw998@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL

# Paths
PROJECT_ROOT="/scratch/rai/vast1/stewartp"
SCRIPT_DIR="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts"
# UPDATE YAML DIRECTORY PATH HERE
YAML_DIR="$PROJECT_ROOT/BIO-465-Capstone-Project/prep_files/boltz_ready/control_tests"

# Create log directories
mkdir -p "$PROJECT_ROOT/logs/boltz_array"

# Generate YAML list file
YAML_LIST="$PROJECT_ROOT/yaml_list.txt"
ls "$YAML_DIR"/*.yaml > "$YAML_LIST"
NUM_YAML=$(wc -l < "$YAML_LIST")
echo "Found $NUM_YAML YAML files in $YAML_DIR"
echo "YAML list saved to $YAML_LIST"

# SLURM array chunk size (must be <= 1000)
CHUNK_SIZE=50

for (( i=0; i<$NUM_YAML; i+=CHUNK_SIZE )); do
    START=$i
    END=$(( i + CHUNK_SIZE - 1 ))
    if [ $END -ge $NUM_YAML ]; then
        END=$(( NUM_YAML - 1 ))
    fi

    echo "Submitting array tasks $START to $END"

    sbatch --array=$START-$END%5 \
           --export=ALL,PROJECT_ROOT="$PROJECT_ROOT",YAML_LIST="$YAML_LIST",SCRIPT_DIR="$SCRIPT_DIR" \
           --output="$PROJECT_ROOT/logs/boltz_array/task_%A_%a.log" \
           --error="$PROJECT_ROOT/logs/boltz_array/task_%A_%a.log" \
           "$SCRIPT_DIR/boltz_array.sh"
done