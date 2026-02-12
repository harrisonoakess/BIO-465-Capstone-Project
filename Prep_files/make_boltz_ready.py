#!/usr/bin/env python3
import argparse
import csv
import random
import re
from datetime import datetime
from pathlib import Path


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


def make_yaml(protein_seq: str, ligand: dict) -> str:
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

    return "\n".join(lines) + "\n"



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x_proteins", type=int, required=True)
    ap.add_argument("--y_ceramides", type=int, required=True)
    ap.add_argument("--random", action="store_true", help="randomly sample instead of first X/Y")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    proteome_csv = Path("output_files/proteome.csv")
    ceramides_csv = Path("output_files/ceramides.csv")

    if not proteome_csv.exists():
        raise FileNotFoundError(f"Missing {proteome_csv}")
    if not ceramides_csv.exists():
        raise FileNotFoundError(f"Missing {ceramides_csv}")

    proteins = read_proteins(proteome_csv)
    ceramides = read_ceramides(ceramides_csv)

    if args.x_proteins > len(proteins):
        raise ValueError(f"x_proteins={args.x_proteins} > proteins available ({len(proteins)})")
    if args.y_ceramides > len(ceramides):
        raise ValueError(f"y_ceramides={args.y_ceramides} > ceramides available ({len(ceramides)})")

    if args.random:
        rng = random.Random(args.seed)
        proteins = rng.sample(proteins, k=args.x_proteins)
        ceramides = rng.sample(ceramides, k=args.y_ceramides)
    else:
        proteins = proteins[:args.x_proteins]
        ceramides = ceramides[:args.y_ceramides]

    run_name = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    out_dir = Path("boltz_ready") / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write X*Y yaml files
    n = 0
    for p in proteins:
        for c in ceramides:
            fname = f"{safe_name(p['accession'])}__{safe_name(c['ligand_id'])}.yaml"
            (out_dir / fname).write_text(make_yaml(p["sequence"], c), encoding="utf-8")
            n += 1

    print(f"Created {n} YAML files in: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
