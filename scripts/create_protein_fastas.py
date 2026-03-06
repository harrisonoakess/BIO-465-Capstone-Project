#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path

def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")

def main():
    ap = argparse.ArgumentParser(description="Convert proteome CSV to one FASTA per protein.")
    ap.add_argument("--proteome_csv", type=Path, required=True,
                    help="CSV containing columns: accession, sequence (extra columns OK)")
    ap.add_argument("--out_dir", type=Path, required=True,
                    help="Output directory for per-protein FASTA files")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    wrote = 0
    skipped = 0

    with open(args.proteome_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        if "accession" not in fields or "sequence" not in fields:
            raise ValueError(f"CSV must include 'accession' and 'sequence'. Found: {fields}")

        for row in reader:
            acc = (row.get("accession") or "").strip()
            seq = (row.get("sequence") or "").strip().replace(" ", "")

            if not acc or not seq:
                skipped += 1
                continue

            # Basic sequence validation
            if not re.fullmatch(r"[A-Za-z*\-\.]+", seq):
                skipped += 1
                continue

            out_path = args.out_dir / f"{safe_name(acc)}.fasta"
            out_path.write_text(f">{acc}\n{seq}\n", encoding="utf-8")
            wrote += 1

    print(f"Wrote {wrote} FASTA files to: {args.out_dir.resolve()}")
    if skipped:
        print(f"Skipped {skipped} rows (missing/invalid accession or sequence).")

if __name__ == "__main__":
    main()