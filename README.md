# Reproducing the Data with the Pipeline Scripts

This project can be reproduced using the provided shell pipelines.

## What the pipelines do

The main pipeline handles:

1. Preparing protein inputs
2. Generating YAML files
3. Submitting Boltz-2 jobs

A second pipeline handles downstream analysis after Boltz outputs are available.

---

## Before You Start

Set your local paths in:

    capstone_path_env.sh

Make sure the paths used by the pipelines are correct for your system.

At minimum, check these variables:

- `PROJECT_ROOT`
- `FASTA_FILE`
- `CSV_FILE`
- `LIGAND_DIR`
- `YAML_DIR`
- `MSA_BASE_DIR`
- `PROCESSED_DIR`
- `PLOT_DIR`

---

## Pipeline 1: Prepare Inputs, Generate YAMLs, and Submit Boltz Jobs

Run this pipeline to prepare the data and launch Boltz jobs.

### Manual protein CSV mode

    bash run_pipeline.sh \
      --protein_csv /path/to/proteins.csv \
      --ligand_csv /path/to/ligands.csv

### Proteome mode

    bash run_pipeline.sh \
      --proteome \
      --ligand_csv /path/to/ligands.csv

### With optional extra SMILES

If you want to include an extra SMILES ligand from a TXT file, add `--smiles_txt`:

    bash run_pipeline.sh \
      --protein_csv /path/to/proteins.csv \
      --ligand_csv /path/to/ligands.csv \
      --smiles_txt /path/to/cofactor.txt

### Dry run

To test the pipeline without submitting Boltz jobs:

    bash run_pipeline.sh \
      --protein_csv /path/to/proteins.csv \
      --ligand_csv /path/to/ligands.csv \
      --dry-run

---

## Required Input Files

### Protein CSV

The protein CSV should contain the proteins you want to run.

### Ligand CSV

The ligand CSV should contain the ligands you want to compare.

### Optional SMILES TXT

If used, the TXT file should contain one SMILES string.

### MSA folders

The pipeline expects MSA files under the base directory defined by `MSA_BASE_DIR`.

---

## What Pipeline 1 Produces

Running `run_pipeline.sh` will:

- optionally download the proteome FASTA
- optionally convert FASTA to protein CSV
- generate Boltz-ready YAML files
- submit Boltz jobs to the HPC cluster

---

## Pipeline 2: Process Outputs and Generate Analysis

After Boltz jobs finish, run the analysis pipeline.

    bash generate_graphs.sh

This pipeline is used to:

- parse raw Boltz outputs into processed CSV files
- run enrichment analysis
- generate downstream analysis outputs

---

## Full Reproduction Order

Run the steps in this order:

### 1. Configure paths

Edit:

    capstone_path_env.sh

### 2. Run the main Boltz pipeline

    bash run_pipeline.sh \
      --protein_csv /path/to/proteins.csv \
      --ligand_csv /path/to/ligands.csv

or:

    bash run_pipeline.sh \
      --proteome \
      --ligand_csv /path/to/ligands.csv

### 3. Wait for Boltz jobs to finish

Make sure all submitted jobs complete successfully before continuing.

### 4. Run the analysis pipeline

    bash run_analysis_pipeline.sh

---

## Notes

- Use `--smiles_txt` only when you want to include the extra SMILES ligand.
- If `--smiles_txt` is omitted, no extra SMILES is used.
- If processed CSVs are already available, the analysis pipeline can be run after Boltz outputs are prepared.
- The main pipeline and the analysis pipeline are intended to be run separately.