#!/bin/bash
#SBATCH --job-name=boltz_control_tests
#SBATCH --output=../logs/boltz_%j.log
#SBATCH --error=../logs/boltz_%j.log
#SBATCH --time=24:00:00
#SBATCH --partition=notchpeak-gpu
#SBATCH --qos=notchpeak-gpu
#SBATCH --account=notchpeak-gpu
#SBATCH --gres=gpu:2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --mail-user=mander19@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL

# Gres Type that work on Notchpeak: a100
# Potential GPUs: l40, rtx6000, a800, a6000, a40, 3090, a5500

module purge
module load boltz2

nvidia-smi

boltz predict ../prep_files/boltz_ready/control_tests \
    --use_msa_server \
    --num_workers 8 \
    --out_dir ../outputs \
    --override