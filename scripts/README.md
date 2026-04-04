## BIO 465 Capstone: Exploring Protein-Ligand Interactions Across the Proteome via Boltz-2

BYU Winter 2026 Capstone Project created by Amanda Warren, Harrison Oakes, and Matthew Anderson

Sponsored by Dr. Paul Stewart at the Huntsman Cancer Institute

Significant data contributions from Kevin Hicks, PhD and Morgana Contini, PhD Candidate

## Input Data


## Workflow
1. Prep data: Input data goes into input folders in the form of csv or fasta / download the proteome if necessary

MSA file generation is optional here -- I think performance is fine by just calling the local msa server

2. make_boltz_ready.py: Generate .yaml files for each protein-ligand combination
3. Run boltz on the yaml files
4. output_parsing_to_csv: Creates a CSV file of all of the results
5. Plots: 
    - Enrichment
    - Density heat scatterplot
    - Boxplots

## Results
Explain affinity, prediction, which tags are necessary here
Which files are important? .cif, .a3m, etc.

## Storage
Results are stored in the U of U HPC scratch space in /scratch/rai/vast1/stewartp

## HPC Usage
If you have difficulties with the Utah HPC or need to get set up, go to https://www.chpc.utah.edu/ or email helpdesk@chpc.utah.edu

## FAQ