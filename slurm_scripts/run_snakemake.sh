#!/bin/csh

#SBATCH --job-name=run_snakemake
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --cluster=granite
#SBATCH --partition=rai-gpu-grn
#SBATCH --qos=rai-gpu-grn
#SBATCH --account=rai
#SBATCH --mem=8G
#SBATCH --time=72:00:00
#SBATCH --output=logs/snakemake_%A.log
#SBATCH --requeue

# Set Data and Working Directories

setenv WORKDIR /uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project

setenv SCRDIR $WORKDIR/scripts
mkdir -p $SCRDIR
cp -r $WORKDIR/* $SCRDIR
cd $SCRDIR 

# Load modules
module purge
module load snakemake/9.3.3

# Run the program
# snakemake   --jobs 500 \
#             --executor slurm \
#             --resources mem_mb=100000 runtime=4320 \
#             --rerun-incomplete \
#             --latency-wait 30 \
#             --cluster "sbatch --time={resources.time} --nodes={resources.nodes} --ntasks={threads}" \
#             --snakefile Snakefile \
#             --directory $SCRDIR \
#             --printshellcmds
   
snakemake --jobs 500 \
          --rerun-incomplete \
          --latency-wait 30 \
          --snakefile Snakefile \
          --directory $SCRDIR \
          --printshellcmds \
          --cluster "sbatch \
--partition=rai-gpu-grn \
--qos=rai-gpu-grn \
--account=rai \
--cpus-per-task={threads} \
--mem={resources.mem_mb} \
--gres=gpu:{resources.gpu} \
--time={resources.time} \
--output=logs/%x_%j.out \
--error=logs/%x_%j.err"
