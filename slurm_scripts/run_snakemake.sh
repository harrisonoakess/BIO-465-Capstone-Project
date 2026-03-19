#!/bin/bash

#SBATCH --job-name=run_snakemake
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mem=8G
#SBATCH --time=72:00:00
#SBATCH --output=logs/snakemake_%A.log
#SBATCH --error=logs/snakemake_%A.log
#SBATCH --requeue

cd /uufs/chpc.utah.edu/common/home/u6073680/Capstone/BIO-465-Capstone-Project/scripts

# Load modules
module purge
module load snakemake
   
snakemake --jobs 500 \
          --cluster "sbatch {resources.gpu_flag} --cpus-per-task={threads} --mem={resources.mem_mb}" \
          --rerun-incomplete \
          --latency-wait 30 \
          --snakefile Snakefile
