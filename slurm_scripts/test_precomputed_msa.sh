#!/bin/bash
#SBATCH --job-name=short_rai_test
#SBATCH --output=../logs/rai_precomputed_msa_%j.log
#SBATCH --error=../logs/rai_precomputed_msa_%j.log
#SBATCH --time=02:00:00
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn-short
#SBATCH --account=rai
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G     
#SBATCH --mail-user=aw998@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL

set -euo pipefail

# Load Boltz module
module purge
module load boltz2

# Input YAML and output directory
export YAML_FILE="../prep_files/test_yaml/test.yaml"
export OUTPUT_DIR="/scratch/rai/vast1/stewartp/test_boltz"

mkdir -p "$OUTPUT_DIR"

# Run Boltz using GPU
boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold02.int.chpc.utah.edu:8088 \
    --out_dir "$OUTPUT_DIR"