#!/bin/bash
#SBATCH --job-name=msa_gpu_test
#SBATCH --output=../logs/precomputed_msa_%j.log
#SBATCH --error=../logs/precomputed_msa_%j.log
#SBATCH --time=08:00:00
#SBATCH --cluster=notchpeak
#SBATCH --partition=notchpeak-gpu
#SBATCH --qos=notchpeak-gpu
#SBATCH --account=notchpeak-gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G     

# Load Boltz module
module purge
module load boltz2

# Input YAML and output directory
export YAML_FILE="../prep_files/test_yaml/test.yaml"
export OUTPUT_DIR="../test_output/boltz"

# Run Boltz using GPU
boltz predict "$YAML_FILE" \
    --use_msa_server \
    --msa_server_url=http://colabfold02.int.chpc.utah.edu:8088 \
    --out_dir "$OUTPUT_DIR"