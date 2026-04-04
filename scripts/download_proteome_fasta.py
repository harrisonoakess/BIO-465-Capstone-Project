#!/usr/bin/env python3
from pathlib import Path
import requests
import argparse

UNIPROT_STREAM_URL = "https://rest.uniprot.org/uniprotkb/stream"


def download_proteome_fasta(proteome_id: str, out_path: Path) -> None:
    params = {
        "query": f"(organism_id:9606) AND (proteome:{proteome_id}) AND (reviewed:true) AND (is_isoform:false)",
        "format": "fasta",
        "compressed": "false",
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = out_path.with_suffix(".tmp")

    with requests.get(UNIPROT_STREAM_URL, params=params, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    tmp_path.rename(out_path)


def main():
    parser = argparse.ArgumentParser(description="Download UniProt proteome FASTA")
    parser.add_argument("--proteome_id", required=True, help="UniProt proteome ID (e.g., UP000005640)")
    parser.add_argument("--output", required=True, help="Output FASTA file path")

    args = parser.parse_args()

    proteome_id = args.proteome_id
    fasta_path = Path(args.output)

    if fasta_path.exists() and fasta_path.stat().st_size > 0:
        print(f"Using cached {fasta_path.resolve()}")
        return

    print(f"Downloading proteome {proteome_id} -> {fasta_path} ...")
    download_proteome_fasta(proteome_id, fasta_path)
    print("Download complete.")


if __name__ == "__main__":
    main()