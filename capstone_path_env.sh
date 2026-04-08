### INSTRUCTIONS
# This script defines the path variables to simplify
# other scripts and allow for quick changes. Run this
# as follows to make the variables available

# source /path/to/capstone_path_env.sh

### PATHS
# Modify this to point to the local project directory
export PROJECT_ROOT="/Users/matthewanderson/Documents/School/Winter 2026/BIO 465/Test_Env/BIO-465-Capstone-Project"

export SLURM_SCRIPT_DIR="$PROJECT_ROOT/slurm_scripts"
export SCRIPT_DIR="$PROJECT_ROOT/scripts"
export YAML_DIR="$PROJECT_ROOT/yaml_files"
export LOG_DIR="$PROJECT_ROOT/logs"
export YAML_LIST_DIR="$PROJECT_ROOT/yaml_lists"
export PROCESSED_DIR="$PROJECT_ROOT/Capstone_TA_Files/processed_outputs"
export SOURCE_DIR="$PROJECT_ROOT/Capstone_TA_Files"
export PLOT_DIR="$PROJECT_ROOT/plots"
export MSA_BASE_DIR="/scratch/rai/vast1/stewartp/msa_per_protein/proteome"

# SCRATCH_ROOT is the location for outputs. If not
# using the University of Utah HPC, this can be set
# to the PROJECT_ROOT or another local directory
export SCRATCH_ROOT="/scratch/rai/vast1/stewartp"

export OUTPUT_DIR="$SCRATCH_ROOT/boltz_results"