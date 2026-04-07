#!/usr/bin/env python3

from pathlib import Path
import argparse
import re


def sanitize_name(name: str) -> str:
    """Replace any unsafe filesystem characters with underscores."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def main():
    parser = argparse.ArgumentParser(
        description="Split a multi-sequence FASTA into individual FASTA files named by protein ID."
    )
    parser.add_argument("--fasta_file", type=Path, required=True, help="Input FASTA")
    parser.add_argument("--out_dir", type=Path, required=True, help="Output directory")
    parser.add_argument("--prefix", default="", help="Optional prefix for output files")

    args = parser.parse_args()

    fasta_file = args.fasta_file
    out_dir = args.out_dir
    prefix = args.prefix

    out_dir.mkdir(parents=True, exist_ok=True)

    with open(fasta_file) as f:
        seq_lines = []
        protein_id = None

        for line in f:
            if line.startswith(">"):
                if seq_lines and protein_id:
                    # Write previous sequence to file
                    out_file = out_dir / f"{prefix}{protein_id}.fasta"
                    with open(out_file, "w") as out:
                        out.writelines(seq_lines)

                # Start new sequence
                seq_lines = [line]
                # Extract first word after ">"
                protein_id = line[1:].split()[0]
                protein_id = sanitize_name(protein_id)

            else:
                seq_lines.append(line)

        # Write last sequence
        if seq_lines and protein_id:
            out_file = out_dir / f"{prefix}{protein_id}.fasta"
            with open(out_file, "w") as out:
                out.writelines(seq_lines)

    print(f"FASTA split complete. Files written to {out_dir}")


if __name__ == "__main__":
    main()