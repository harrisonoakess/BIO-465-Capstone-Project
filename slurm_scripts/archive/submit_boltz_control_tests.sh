module load boltz2

# Paths
# PROJECT_ROOT="/scratch/rai/vast1/stewartp"
PROJECT_ROOT="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project"
SCRIPT_DIR="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts"
# UPDATE YAML DIRECTORY PATH HERE
YAML_DIR="$PROJECT_ROOT/prep_files/boltz_ready/control_tests"

# Create log directories
mkdir -p "$PROJECT_ROOT/logs/boltz_array"

# Generate YAML list file
YAML_LIST="$PROJECT_ROOT/yaml_list_control_tests.txt"
ls "$YAML_DIR"/*.yaml > "$YAML_LIST"
NUM_YAML=$(wc -l < "$YAML_LIST")
echo "Found $NUM_YAML YAML files in $YAML_DIR"
echo "YAML list saved to $YAML_LIST"

sbatch \
  --job-name=control_tests \
  --time=02:00:00 \
  --cluster=granite \
  --partition=rai-gpu-grn \
  --qos=rai-gpu-grn \
  --account=rai \
  --mail-user=mander19@byu.edu \
  --mail-type=BEGIN,END,FAIL \
  --array=0-99%5 \
  --export=ALL,PROJECT_ROOT="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project",YAML_LIST="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/yaml_list_control_tests.txt",SCRIPT_DIR="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts",JOB_NAME="control_tests" \
  --output="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/logs/boltz_array/task_%A_%a.log" \
  --error="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/logs/boltz_array/task_%A_%a.log" \
  "/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts/boltz_array.sh"
