#!/bin/bash
#SBATCH --output=/scratch/u6073678/logs/test_%j.log
#SBATCH --error=/scratch/u6073678/logs/test_%j.log
#SBATCH --partition=notchpeak-shared-short
#SBATCH --qos=notchpeak-shared-short
#SBATCH --account=notchpeak-shared-short
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --time=00:01:00

set -euo pipefail

mkdir -p /scratch/u6073678/logs

echo "Job started"
pwd
ls -l
echo "Job finished"