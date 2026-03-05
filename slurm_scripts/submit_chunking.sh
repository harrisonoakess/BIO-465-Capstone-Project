#!/bin/bash
#SBATCH --job-name=chunk_proteome
#SBATCH --output=../logs/chunk_proteome_%j.log
#SBATCH --error=../logs/chunk_proteome_%j.log
#SBATCH --time=00:10:00
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn-short
#SBATCH --account=rai
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

# Load Python module
module purge
module load python

# Run the Python script
python ../scripts/chunk_proteome.py

