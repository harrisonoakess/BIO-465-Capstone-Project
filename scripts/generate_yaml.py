import argparse
import re
from pathlib import Path

NADPH_SMILES = "NC(=O)C1=CN(C=CC1)[C@@H]1O[C@H](COP(O)(=O)OP(O)(=O)OC[C@H]2O[C@H]([C@H](OP(O)(O)=O)[C@@H]2O)N2C=NC3=C2N=CN=C3N)[C@@H](O)[C@H]1O"

def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")

def read_fasta(fasta_file: Path):
    seq_lines = []
    name = fasta_file.stem

    with open(fasta_file) as f:
        for line in f:
            if line.startswith(">"):
                continue
            seq_lines.append(line.strip())

    sequence = "".join(seq_lines)

    return name, sequence

def make_yaml(protein_name, protein_seq, msa_path, ligand):
    lines = []

    lines.append("version: 1")
    lines.append(f"title: {protein_name}")
    lines.append("sequences:")

    lines.append("  - protein:")
    lines.append("      id: A")
    lines.append(f"      sequence: {protein_seq}")
    lines.append(f"      msa: {msa_path}")

    lines.append("  - ligand:")
    lines.append("      id: B")

    if ligand["type"] == "ccd":
        lines.append(f"      ccd: {ligand['value']}")
    else:
        v = ligand["value"].replace("'", "''")
        lines.append(f"      smiles: '{v}'")

    lines.append("  - ligand:")
    lines.append("      id: C")
    lines.append(f"      smiles: '{NADPH_SMILES}'")

    lines.append("properties:")
    lines.append("  - affinity:")
    lines.append("      binder: B")

    return "\n".join(lines) + "\n"


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--fasta_file", type=Path, required=True)
    parser.add_argument("--msa_file", type=Path, required=True)

    parser.add_argument("--ligand_id", required=True)
    parser.add_argument("--ligand_type", required=True)
    parser.add_argument("--ligand_value", required=True)

    parser.add_argument("--output_yaml", type=Path, required=True)

    args = parser.parse_args()

    protein_name, sequence = read_fasta(args.fasta_file)

    ligand = {
        "ligand_id": args.ligand_id,
        "type": args.ligand_type,
        "value": args.ligand_value
    }

    yaml_text = make_yaml(protein_name, sequence, args.msa_file, ligand)

    args.output_yaml.parent.mkdir(parents=True, exist_ok=True)
    args.output_yaml.write_text(yaml_text)


if __name__ == "__main__":
    main()