import os
import pandas as pd
from pathlib import Path
import csv
import re
import random
import hashlib

# script_dir = Path(__file__).parent.resolve()
# data_dir = Path('../prep_files/output_files/')
# yaml_dir = Path('../prep_files/boltz_ready/')

PROJECT_ROOT = Path(os.environ["PROJECT_ROOT"])
SCRIPT_DIR = Path(os.environ["SCRIPT_DIR"])
YAML_DIR = Path(os.environ["YAML_DIR"])
OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
SOURCE_DIR = Path(os.environ["SOURCE_DIR"])

def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")

def make_ligand_id(smiles):
    if isinstance(smiles, float) or smiles is None:
        return None
    
    id = hashlib.sha256(smiles.encode('utf-8')).hexdigest()
    return id[:16]

def make_control_protein_ligand_csv(output_name):
    data_name = 'AID_977608_datatable_all.csv'
    reference_name = 'pdb_chain_uniprot.csv'
    proteome_name = 'proteome.csv'

    data = pd.read_csv(SOURCE_DIR / data_name)
    reference = pd.read_csv(SOURCE_DIR / reference_name, comment='#', low_memory=False)
    proteome = pd.read_csv(SOURCE_DIR / proteome_name)

    data['PDB'] = data['PDB'].str.lower()
    reference['PDB'] = reference['PDB'].str.lower()

    data = data[['PDB', 'PUBCHEM_EXT_DATASOURCE_SMILES', 'IC50', 'Protein Name']]
    reference = reference[['PDB', 'CHAIN', 'SP_PRIMARY']]
    proteome = proteome[['accession', 'sequence']]

    data = data.rename(columns={'PUBCHEM_EXT_DATASOURCE_SMILES': 'SMILES', 'IC50': 'Experimental_Affinity'})
    reference = reference.rename(columns={'SP_PRIMARY': 'accession'})

    chain_counts = reference.groupby('PDB')['CHAIN'].nunique()
    monomer_pdbs = chain_counts[chain_counts == 1].index

    data = data[data['PDB'].isin(monomer_pdbs)]

    output = (
        data
        .merge(reference, on='PDB', how='left')
        .merge(proteome, on='accession', how='left')
    )
    
    needed_cols = ['accession', 'Protein Name', 'PDB', 'sequence', 'SMILES', 'ligand_id', 'Experimental_Affinity']

    output = output.drop(columns=['CHAIN'])
    output['ligand_id'] = output['SMILES'].apply(make_ligand_id)
    output = output.dropna(subset=['sequence', 'ligand_id'])
    output = output[needed_cols]
    output = output.sort_values(by=needed_cols, ascending=True)
    output = output.drop_duplicates(subset=needed_cols)

    print(f'Number of unique accessions in output: {output["accession"].nunique()}')
    print(f'Number of unique sequences in output: {output["sequence"].nunique()}')

    output.to_csv(OUTPUT_DIR / output_name, index=False)
    print(f'Wrote {len(output)} control proteins to {output_name}')

def read_yaml_data(csv_path: Path):
    yaml_data = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = (row.get("accession") or "").strip()
            pdb = (row.get("PDB") or "").strip()
            seq = (row.get("sequence") or "").strip()
            smiles = (row.get("SMILES") or "").strip()
            ligand_id = (row.get("ligand_id") or "").strip()
            if acc and pdb and seq and smiles and ligand_id:
                yaml_data.append({"accession": acc, "PDB": pdb, "sequence": seq, "SMILES": smiles, "ligand_id": ligand_id})
    return yaml_data


def make_yaml_files(yaml_data, yaml_dir_name, num_files=None):
    yaml_dir_path = YAML_DIR / yaml_dir_name
    yaml_dir_path.mkdir(parents=True, exist_ok=True)
    file_delim = "__"

    if num_files is not None:
        rng = random.Random(42)
        rng.shuffle(yaml_data)
        yaml_data = yaml_data[:num_files]

    for row in yaml_data:
        acc = row['accession']
        pdb = row['PDB']
        sequence = row['sequence']
        smiles = row['SMILES']
        ligand_id = row['ligand_id']

        yaml_content = make_yaml_contents(sequence, {'type': 'smiles', 'value': smiles})
        
        yaml_file_path = yaml_dir_path / f'{pdb}{file_delim}{ligand_id}.yaml'
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
    print(f'Wrote {len(yaml_data)} YAML file(s) to {yaml_dir_path}')


def make_yaml_contents(protein_seq: str, ligand: dict) -> str:
    lines = []
    lines.append("version: 1")
    lines.append("sequences:")
    lines.append("  - protein:")
    lines.append("      id: A")
    lines.append(f"      sequence: {protein_seq}")
    lines.append("  - ligand:")
    lines.append("      id: B")

    if ligand["type"] == "ccd":
        lines.append(f"      ccd: {ligand['value']}")
    else:
        v = ligand["value"].replace("'", "''")
        lines.append(f"      smiles: '{v}'")

    lines.append("properties:")
    lines.append("  - affinity:")
    lines.append("      binder: B")  # must match ligand id

    return "\n".join(lines) + "\n"


def main():
    output_csv_name = 'control_proteins.csv'

    if not (OUTPUT_DIR / output_csv_name).exists():
        make_control_protein_ligand_csv(output_csv_name)

    make_control_protein_ligand_csv(output_csv_name)

    yaml_data = read_yaml_data(OUTPUT_DIR / output_csv_name)
    print(f'Read {len(yaml_data)} rows from {output_csv_name}')

    yaml_dir_name = 'control_tests'
    # make_yaml_files(yaml_data, yaml_dir_name, 100)
    make_yaml_files(yaml_data, yaml_dir_name)


if __name__ == '__main__':
    main()
