import pandas as pd
from pathlib import Path
import csv
import re
import random

script_dir = Path(__file__).parent.resolve()
data_dir = Path('../prep_files/output_files/')
yaml_dir = Path('../prep_files/boltz_ready/')

def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")

def make_control_protein_ligand_csv(output_name):
    data_name = 'AID_977608_datatable_all.csv'
    reference_name = 'pdb_chain_uniprot.csv'
    proteome_name = 'proteome.csv'

    data = pd.read_csv(script_dir / data_dir / data_name)
    reference = pd.read_csv(script_dir / data_dir / reference_name, comment='#', low_memory=False)
    proteome = pd.read_csv(script_dir / data_dir / proteome_name)

    data['PDB'] = data['PDB'].str.lower()
    reference['PDB'] = reference['PDB'].str.lower()

    data = data[['PDB', 'PUBCHEM_EXT_DATASOURCE_SMILES', 'IC50', 'Protein Name']]
    reference = reference[['PDB', 'CHAIN', 'SP_PRIMARY']]
    proteome = proteome[['accession', 'sequence']]

    chain_counts = reference.groupby('PDB')['CHAIN'].nunique()
    monomer_pdbs = chain_counts[chain_counts == 1].index

    data = data[data['PDB'].isin(monomer_pdbs)]

    output = (
        data
        .merge(reference, on='PDB', how='left')
        .merge(proteome, left_on='SP_PRIMARY', right_on='accession', how='left')
        .rename(columns={'SP_PRIMARY': 'UniProt', 
                         'IC50': 'Affinity',
                         'PUBCHEM_EXT_DATASOURCE_SMILES': 'SMILES'})
    )
    
    output = output.drop(output.index[0:4])
    output = output.drop(columns=['CHAIN', 'UniProt'])
    output = output.dropna(subset=['sequence'])
    output = output.reset_index(drop=True)

    output.to_csv(script_dir / data_dir / output_name, index=False)
    print(f'Wrote {len(output)} control proteins to {output_name}')

def read_yaml_data(csv_path: Path):
    yaml_data = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = (row.get("accession") or "").strip()
            protein_name = (row.get("Protein Name") or "").strip()
            seq = (row.get("sequence") or "").strip()
            smiles = (row.get("SMILES") or "").strip()
            if acc and protein_name and seq and smiles:
                yaml_data.append({"accession": acc, "Protein Name": protein_name, "sequence": seq, "SMILES": smiles})
    return yaml_data


def make_yaml_files(yaml_data, yaml_dir_name, num_files=None):
    
    yaml_dir_path = script_dir / yaml_dir / yaml_dir_name
    yaml_dir_path.mkdir(parents=True, exist_ok=True)

    if num_files is not None:
        rng = random.Random(42)
        rng.shuffle(yaml_data)
        yaml_data = yaml_data[:num_files]

    for row in yaml_data:
        acc = row['accession']
        protein_name = row['Protein Name']
        sequence = row['sequence']
        smiles = row['SMILES']

        yaml_content = make_yaml_contents(sequence, {'type': 'smiles', 'value': smiles})
        
        yaml_file_path = yaml_dir_path / f'{acc}_{safe_name(protein_name)}.yaml'
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        print(f'Wrote YAML file for {protein_name} ({acc}) to {yaml_file_path}')


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

    if not (script_dir / data_dir / output_csv_name).exists():
        make_control_protein_ligand_csv(output_csv_name)

    make_control_protein_ligand_csv(output_csv_name)

    yaml_data = read_yaml_data(script_dir / data_dir / output_csv_name)
    print(f'Read {len(yaml_data)} rows from {output_csv_name}')

    yaml_dir_name = 'control_tests'
    make_yaml_files(yaml_data, yaml_dir_name, 50)

    
if __name__ == '__main__':
    main()

