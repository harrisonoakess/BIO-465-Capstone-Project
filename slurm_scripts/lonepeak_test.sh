#!/bin/bash
#SBATCH --job-name=boltz_h100
#SBATCH --output=../logs/boltz_%j.log
#SBATCH --error=../logs/boltz_%j.log
#SBATCH --time=02:00:00
#SBATCH --partition=lonepeak-gpu
#SBATCH --qos=lonepeak-gpu
#SBATCH --account=lonepeak-gpu
#SBATCH --gres=gpu:1080ti:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
    
# Gres Type that work on kingspeak: 1080ti

# It looks like the Lone Peak GPUs don't work with the PyTorch

module purge
module load boltz2

nvidia-smi

boltz predict ../prep_files/boltz_ready/run_20260212_142921/A0A087WVL8__CER_C2_N_acetyl_sphingosine.yaml \
    --use_msa_server \
    --num_workers 8 \
    --out_dir ../outputs \
    --override