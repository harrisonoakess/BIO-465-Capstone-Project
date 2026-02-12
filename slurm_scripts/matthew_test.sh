#!/bin/bash
#SBATCH --job-name=boltz_h100
#SBATCH --output=../logs/boltz_%j.log
#SBATCH --error=../logs/boltz_%j.log
#SBATCH --time=02:00:00
#SBATCH --partition=granite-gpu-guest
#SBATCH --qos=granite-gpu-guest
#SBATCH --account=stewartp
#SBATCH --gres=gpu:4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

module purge
module load boltz2

nvidia-smi

boltz predict ../../boltz/examples/cyclic_prot.yaml \
    --use_msa_server \
    --num_workers 4 \
    --out_dir ../outputs