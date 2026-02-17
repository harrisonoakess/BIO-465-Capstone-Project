#!/bin/bash
#SBATCH --job-name=boltz_paul_met_whole_prot_seq
#SBATCH --output=../logs/boltz_%j.log
#SBATCH --error=../logs/boltz_%j.log
#SBATCH --time=48:00:00
#SBATCH --partition=notchpeak-gpu
#SBATCH --qos=notchpeak-gpu
#SBATCH --account=notchpeak-gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G

# Gres Type that work on Notchpeak: a100
# Potential GPUs: l40, rtx6000, a800, a6000, a40, 3090, a5500

module purge
module load boltz2

nvidia-smi

YAML_DIR="${1:-../prep_files/boltz_ready/paul_metabolites_whole_proteome}"

find "$YAML_DIR" \
    -type f \
    -exec boltz predict "$YAML_DIR" \
    --use_msa_server \
    --num_workers 4 \
    --out_dir ../outputs \
    --override \;
