sbatch \
  --job-name=control_tests \
  --time=00:10:00 \
  --cluster=granite \
  --partition=rai-gpu-grn \
  --qos=rai-gpu-grn \
  --account=rai \
  --mail-user=aw998@byu.edu \
  --mail-type=BEGIN,END,FAIL \
  --array=0-49%5 \
  --export=ALL,PROJECT_ROOT="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project",YAML_LIST="yaml_list.txt",SCRIPT_DIR="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts",JOB_NAME="control_tests" \
  --output="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/logs/boltz_array/task_%A_%a.log" \
  --error="/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/logs/boltz_array/task_%A_%a.log" \
  "/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/slurm_scripts/boltz_array.sh"
