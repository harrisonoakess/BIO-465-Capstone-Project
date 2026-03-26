module load boltz2

JOB_NAME="control_tests"

# Paths
SCRATCH_ROOT="/scratch/rai/vast1/stewartp"
PROJECT_ROOT="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project"
SCRIPT_DIR="$PROJECT_ROOT/slurm_scripts"
OUTPUT_DIR="$SCRATCH_ROOT/boltz_results/$JOB_NAME"
YAML_DIR="$PROJECT_ROOT/prep_files/boltz_ready/$JOB_NAME"
LOG_DIR="$PROJECT_ROOT/logs/boltz_array$JOB_NAME"
YAML_LIST_FOLDER="$PROJECT_ROOT/slurm_scripts/yaml_lists"

# Make directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$YAML_LIST_FOLDER"

# Generate YAML list file
YAML_LIST="$YAML_LIST_FOLDER/yaml_list_$JOB_NAME.txt"
ls "$YAML_DIR"/*.yaml > "$YAML_LIST"
NUM_YAML=$(wc -l < "$YAML_LIST")
echo "Found $NUM_YAML YAML files in $YAML_DIR"
echo "YAML list saved to $YAML_LIST"

MAX_ARRAY_INDEX=$((NUM_YAML - 1))

sbatch \
  --job-name=$JOB_NAME \
  --time=02:00:00 \
  --cluster=granite \
  --partition=rai-gpu-grn \
  --qos=rai-gpu-grn \
  --account=rai \
  --mail-user=mander19@byu.edu \
  --mail-type=BEGIN,END,FAIL \
  --array=0-$MAX_ARRAY_INDEX%5 \
  --export=ALL,PROJECT_ROOT="$PROJECT_ROOT",YAML_LIST="$YAML_LIST",JOB_NAME="$JOB_NAME",OUTPUT_DIR="$OUTPUT_DIR" \
  --output="$LOG_DIR/task_%A_%a.log" \
  --error="$LOG_DIR/task_%A_%a.log" \
  "$SCRIPT_DIR/boltz_array.sh"
