#!/usr/bin/env python3
"""
make_boltz_ready.py

CHANGES (compared to your original):
1) Added CLI args:
   - --msa_base_dir (required): base folder where per-protein MSAs live
   - --out_base_dir (optional): where to write boltz_ready output (default: boltz_ready)
   - --require_msa (optional): if set, error if msa.a3m doesn't exist for a protein
2) Updated make_yaml(...) to accept msa_path and write:
      msa: <path>
   under the protein block.
3) Updated output directory creation to use --out_base_dir.
4) In the YAML-writing loop, compute MSA path per protein:
      <msa_base_dir>/<safe_accession>/msa.a3m
   and pass it into make_yaml(...).
"""

import argparse
import csv
import random
import re
from datetime import datetime
from pathlib import Path

NADH_SMILES = "NC(=O)C1=CN([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)OC[C@H]3O[C@@H](n4cnc5c(N)ncnc54)[C@H](O)[C@@H]3O)[C@@H](O)[C@H]2O)C=CC1"
NADPH_SMILES = "NC(=O)C1=CN(C=CC1)[C@@H]1O[C@H](COP(O)(=O)OP(O)(=O)OC[C@H]2O[C@H]([C@H](OP(O)(O)=O)[C@@H]2O)N2C=NC3=C2N=CN=C3N)[C@@H](O)[C@H]1O"


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")


def read_proteins(csv_path: Path):
    proteins = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = (row.get("accession") or "").strip()
            seq = (row.get("sequence") or "").strip()
            if acc and seq:
                proteins.append({"accession": acc, "sequence": seq})
    return proteins


def read_ceramides(csv_path: Path):
    ligands = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lid = (row.get("ligand_id") or "").strip()
            ltype = (row.get("type") or "").strip().lower()
            val = (row.get("value") or "").strip()
            if lid and ltype and val:
                ligands.append({"ligand_id": lid, "type": ltype, "value": val})
    return ligands


# CHANGE #2: add msa_path param and write "msa: ..." into the protein block
def make_yaml(protein_seq: str, msa_path: str, ligand: dict) -> str:
    lines = []
    lines.append("version: 1")
    lines.append("sequences:")
    lines.append("  - protein:")
    lines.append("      id: A")
    lines.append(f"      sequence: {protein_seq}")
    lines.append(f"      msa: {msa_path}")  # <-- CHANGE: include MSA path
    lines.append("  - ligand:")
    lines.append("      id: B")

    if ligand["type"] == "ccd":
        lines.append(f"      ccd: {ligand['value']}")
    else:
        v = ligand["value"].replace("'", "''")
        lines.append(f"      smiles: '{v}'")

    # Hard-coded NADPH ligand C
    lines.append("  - ligand:")
    lines.append("      id: C")
    lines.append(f"      smiles: '{NADPH_SMILES}'")

    lines.append("properties:")
    lines.append("  - affinity:")
    lines.append("      binder: B")  # must match ligand id

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proteome_csv", type=Path, required=True)
    ap.add_argument("--ceramide_csv", type=Path, required=True)
    ap.add_argument("--output_dir_name", type=str)
    ap.add_argument("--random", action="store_true", help="randomly sample instead of first X/Y")
    ap.add_argument("--seed", type=int, default=7)

    # CHANGE #1: new args for MSA + output base + optional strictness
    ap.add_argument(
        "--msa_base_dir",
        type=Path,
        required=True,
        help="Base dir containing per-protein MSA folders (each should contain msa.a3m). "
             "Example: /scratch/rai/vast1/stewartp/msa_per_protein/proteome",
    )
    ap.add_argument(
        "--out_base_dir",
        type=Path,
        default=Path("boltz_ready"),
        help="Where to write boltz_ready/<run_name> (default: ./boltz_ready)",
    )
    ap.add_argument(
        "--require_msa",
        action="store_true",
        help="If set, raise an error if a protein's msa.a3m file does not exist.",
    )

    args = ap.parse_args()

    # Your existing relative-path behavior: looks for CSVs under scripts/output_files/
    path = Path(__file__).parent / "output_files"
    proteome_csv = path / args.proteome_csv
    ceramides_csv = path / args.ceramide_csv

    if not proteome_csv.exists():
        raise FileNotFoundError(f"Missing {proteome_csv}")
    if not ceramides_csv.exists():
        raise FileNotFoundError(f"Missing {ceramides_csv}")

    proteins = read_proteins(proteome_csv)
    ceramides = read_ceramides(ceramides_csv)

    x_proteins = len(proteins)
    y_ceramides = len(ceramides)

    if args.random:
        rng = random.Random(args.seed)
        proteins = rng.sample(proteins, k=x_proteins)
        ceramides = rng.sample(ceramides, k=y_ceramides)
    else:
        proteins = proteins[:x_proteins]
        ceramides = ceramides[:y_ceramides]

    if args.output_dir_name:
        run_name = args.output_dir_name
    else:
        run_name = datetime.now().strftime("run_%Y%m%d_%H%M%S")

    # CHANGE #3: output folder now uses --out_base_dir
    out_dir = Path(args.out_base_dir) / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    msa_base = args.msa_base_dir

    # CHANGE #4: compute per-protein msa path and pass it to make_yaml()
    n = 0
    file_delim = "__"
    for p in proteins:
        acc_safe = safe_name(p["accession"])
        msa_file = (msa_base / acc_safe / "msa.a3m").resolve()

        if args.require_msa and not msa_file.exists():
            raise FileNotFoundError(f"Missing MSA for {p['accession']}: {msa_file}")

        for c in ceramides:
            fname = f"{safe_name(p['accession'])}{file_delim}{safe_name(c['ligand_id'])}.yaml"
            (out_dir / fname).write_text(
                make_yaml(p["sequence"], str(msa_file), c),
                encoding="utf-8",
            )
            n += 1

    print(f"Created {n} YAML files in: {out_dir.resolve()}")


if __name__ == "__main__":
    main()