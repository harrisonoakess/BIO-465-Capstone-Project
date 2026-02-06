#!/bin/csh

#SBATCH --time=1:00:00          # walltime
#SBATCH --nodes=2               # number of cluster nodes
#SBATCH -o slurm-%j.out-%N      # name of the stdout, using the jobnumber (%j) and the first node (%N)
#SBATCH --ntasks=16             # number of MPI tasks
#SBATCH --account=u6073678      # account
#SBATCH --partition=kingspeak   # partition

# Set Data and Working Directories

setenv WORKDIR $HOME/Capstone   # I don't think this will work w/ symbolic link

setenv SCRDIR /uufs/chpc.utah.edu/common/home/u6073678/Capstone/scripts
mkdir -p $SCRDIR
cp -r $WORKDIR/* $SCRDIR
cd $SCRDIR 

# Load modules
module load python
module load snakemake
module load boltz2

# Run the program
snakemake   --jobs 32 \
            --cluster "sbatch --time={resources.time} --nodes={resources.nodes} --ntasks={threads}" \
            --snakefile Snakefile \
            --directory $SCRDIR \
            --printshellcmds
   

