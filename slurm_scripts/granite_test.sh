#!/bin/bash
#SBATCH --job-name=boltz_h100
#SBATCH --output=../logs/boltz_%j.log
#SBATCH --error=../logs/boltz_%j.log
#SBATCH --time=02:00:00
#SBATCH --partition=granite-gpu-guest
#SBATCH --qos=granite-gpu-guest
#SBATCH --account=stewartp
#SBATCH --gres=gpu:a800:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

# Gres Type that worked on granite: h200, a800, l40s, rtx2000, rtx4500, rtx5000, rtx6000

module purge
module load boltz2

nvidia-smi

boltz predict ../prep_files/boltz_ready/run_20260212_142921/A0A087WVL8__CER_C2_N_acetyl_sphingosine.yaml \
    --use_msa_server \
    --num_workers 8 \
    --out_dir ../outputs \
    --override