import csv
import random
from pathlib import Path

# Paths
pauls_path = Path("output_files/paul_proteins_2.csv")
proteome_path = Path("output_files/proteome.csv")
output_path = Path("output_files/random_plus_paul.csv")

# How many random proteome rows to add
N_RANDOM = 2000

# Optional: make sampling reproducible
RANDOM_SEED = 42


def read_csv_rows(path: Path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    return rows, fieldnames


def normalize_sequence(seq: str) -> str:
    return (seq or "").replace(" ", "").replace("\n", "").strip()


def make_key(row: dict):
    """
    Use accession if present; otherwise fall back to gene+sequence.
    This helps avoid duplicates between Paul's list and proteome.
    """
    accession = (row.get("accession") or "").strip()
    if accession:
        return ("accession", accession)

    gene = (row.get("gene") or "").strip()
    seq = normalize_sequence(row.get("sequence") or "")
    return ("fallback", gene, seq)


def main():
    random.seed(RANDOM_SEED)

    pauls_rows, pauls_fields = read_csv_rows(pauls_path)
    proteome_rows, proteome_fields = read_csv_rows(proteome_path)

    # Use Paul's file columns for the output if possible
    fieldnames = pauls_fields if pauls_fields else proteome_fields

    # Track everything already included from Paul's list
    existing_keys = set()
    combined_rows = []

    for row in pauls_rows:
        key = make_key(row)
        if key not in existing_keys:
            existing_keys.add(key)
            combined_rows.append(row)

    # Filter proteome rows so we don't re-add Paul's proteins
    proteome_candidates = []
    for row in proteome_rows:
        key = make_key(row)
        if key not in existing_keys:
            proteome_candidates.append(row)

    if len(proteome_candidates) < N_RANDOM:
        raise ValueError(
            f"Not enough unique proteome rows to sample {N_RANDOM}. "
            f"Only found {len(proteome_candidates)} candidates."
        )

    sampled_rows = random.sample(proteome_candidates, N_RANDOM)
    combined_rows.extend(sampled_rows)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"Wrote {len(combined_rows)} rows to {output_path}")
    print(f"Included {len(pauls_rows)} rows from Paul's list")
    print(f"Included {len(sampled_rows)} random rows from proteome")


if __name__ == "__main__":
    main()