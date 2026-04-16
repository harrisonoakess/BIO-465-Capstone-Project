# How to do Large-Scale Predictions of Protein-Metabolite Relationships Using our Boltz-2 Pipeline

This guide explains the main steps needed to run the project clearly and in order.

---

## Step 1: Set up the Python environment, install `requirements.txt`, and add *Capstone_TA_Files* to your root directory

Unzip the file we submitted in Learning Suite. Paste the entire folder into the BIO-465-Capstone-Project folder.

This project was tested using a Conda environment with Python 3.11.

Create the environment:

```bash
conda create -n capstone311 python=3.11
```

Activate the environment:

```bash
conda activate capstone311
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include the packages needed by the scripts, such as:

```txt
pandas
numpy
matplotlib
seaborn
scipy
gseapy
mygene
pyrolite
```

---

## Step 2: Set up the path variables in `capstone_path_env.sh`

Before running the scripts, update the environment file so the paths match your machine.

Open:

```bash
capstone_path_env.sh
```

Make sure the variables point to the correct folders.

Example local setup:

```bash
export PROJECT_ROOT="/absolute/path/to/BIO-465-Capstone-Project" # ------MUST CHANGE-------

export SLURM_SCRIPT_DIR="$PROJECT_ROOT/slurm_scripts"
export SCRIPT_DIR="$PROJECT_ROOT/scripts"
export YAML_DIR="$PROJECT_ROOT/yaml_files"
export LOG_DIR="$PROJECT_ROOT/logs"
export YAML_LIST_DIR="$PROJECT_ROOT/yaml_lists"
export PROCESSED_DIR="$PROJECT_ROOT/Capstone_TA_Files/processed_outputs"
export SOURCE_DIR="$PROJECT_ROOT/Capstone_TA_Files"
export PLOT_DIR="$PROJECT_ROOT/plots"

export MSA_BASE_DIR="$PROJECT_ROOT/msa_per_protein"
export SCRATCH_ROOT="$PROJECT_ROOT/scratch"
export OUTPUT_DIR="$SCRATCH_ROOT/boltz_results"
```

### Important variables

- `PROJECT_ROOT` = root of the repository
- `SOURCE_DIR` = folder containing input CSV files
- `YAML_DIR` = where generated YAML files will be written
- `PROCESSED_DIR` = where processed Boltz output CSV files are stored
- `PLOT_DIR` = where figures will be saved

---

## Step 3: Run `generate_TA_data.sh`

This script generates the Boltz YAML input files for the experiment groups.

Run:

```bash
bash generate_TA_data.sh
```

This step should:

- load the source protein and ligand CSV files
- generate YAML files for each protein-ligand combination
- write them into subfolders inside `YAML_DIR`

### Example output folders

- `random_plus_paul_metabolites`
- `random_plus_paul_c16dihydro`
- `pisa_c16dihydro`
- `random_plus_pauls_c16`
- `pisa_c16_human`

After running, you can check the YAML folders with:

```bash
ls yaml_files
```

---

## Step 4: Run `generate_graphs.sh`

This script generates figures from processed prediction CSV files.

**You must exit out of the graph for it to continue to the next because we are using show()**

**Enrichr has a chance of getting Error 429: Too many requests. If this happens, wait a few minutes and try step 4 again. This is not something we can control**

Run:

```bash
bash generate_graphs.sh
```

This step creates plots such as:

- C16 boxplot
- C16 dihydro boxplot
- ceramide heat scatter plots
- enrichment analysis outputs

Plots are written to:

```bash
plots/
```

Enrichment outputs are written under:

```bash
plots/enrichment_analysis/
```

---

## Notes

- `generate_TA_data.sh` is for generating Boltz input YAML files.
- `generate_graphs.sh` is for generating figures from processed CSV outputs.
- Full Boltz job submission requires the HPC/Slurm environment.
- Local testing is mainly for validating paths, generating YAMLs, and creating figures.