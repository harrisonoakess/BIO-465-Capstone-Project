#!/bin/bash
#SBATCH --job-name=boltz_cpu
#SBATCH --output=../logs/boltz_%j.out
#SBATCH --error=../logs/boltz_%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

module load python
module load boltz2

boltz predict ../../boltz/examples/affinity.yaml \
    --use_msa_server \
    --accelerator cpu \
    --devices 1 \
    --num_workers 8 \
    --out_dir ../outputs
