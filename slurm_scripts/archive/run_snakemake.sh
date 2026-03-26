#!/bin/bash

#SBATCH --job-name=run_snakemake
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mem=8G
#SBATCH --time=24:00:00
#SBATCH --output=logs/snakemake_%A.log
#SBATCH --error=logs/snakemake_%A.log
#SBATCH --requeue
#SBATCH --mail-user=aw998@byu.edu
#SBATCH --mail-type=BEGIN,END,FAIL

cd /uufs/chpc.utah.edu/common/home/u6073680/Capstone/BIO-465-Capstone-Project/scripts

# Load modules
module load snakemake
   

# Run Snakemake using SLURM executor
snakemake --jobs 10 \
          --executor slurm \
          --rerun-incomplete \
          --snakefile Snakefile \
          --profile ../scripts/profiles/slurm \
          --default-resources slurm_account=rai slurm_partition=rai-gpu-grn \
          --slurm-qos rai-gpu-grn