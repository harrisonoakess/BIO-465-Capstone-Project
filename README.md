# Capstone Reproducibility Workflow

This repository is organized to support a reproducible workflow for preparing protein and ligand inputs, generating MSAs, and creating YAML files for downstream modeling.

## Overview

The current reproducibility pipeline follows this general process:

1. Download a proteome
   - Upload FASTA
   - Convert FASTA to CSV

2. Convert the CSV into one FASTA file per protein in scratch storage

3. Generate an MSA for each protein and store outputs in scratch

4. Create one YAML file for each protein

5. Add ceramide ligand inputs in a structured, reproducible format

---

## Workflow Steps

### 1. Download proteome

Start by obtaining the proteome FASTA file that will be used as the source input for the pipeline.

#### 1.01 Upload FASTA
Place the proteome FASTA file into the appropriate input location.

#### 1.02 Convert FASTA to CSV
Convert the FASTA file into a CSV format so that proteins can be processed more easily in downstream scripts.

---

### 2. Convert CSV into one FASTA file per protein

Take the protein CSV and generate one FASTA file for each protein sequence.

These FASTA files should be stored in scratch space so they can be used for large-scale batch processing.

---

### 2.1 Generate MSA for each protein

For each protein FASTA file:

- run MSA generation
- save the resulting MSA outputs in scratch storage
- keep naming conventions consistent so each MSA can be matched back to its protein

---

### 3. Create one YAML file for each protein

After the protein FASTA files and MSAs are ready, generate one YAML file per protein.

Each YAML file should point to the required inputs for downstream runs, including protein sequence information and ligand information where needed.

---

### 4. Add ceramide ligand inputs

Ceramide inputs should be stored in a reproducible file format so they can be reused across runs.

A likely approach is to keep ligand information in a dedicated CSV file, then reference it when generating YAML files.

---


```text
project-root/
├── scripts/
└── files/
    ├── ligand_csv/
    ├── protein_csv/
    ├── yaml/
    └── fasta_files/