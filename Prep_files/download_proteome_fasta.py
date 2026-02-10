#!/usr/bin/env python3
from pathlib import Path
import requests

UNIPROT_STREAM_URL = "https://rest.uniprot.org/uniprotkb/stream"


def download_proteome_fasta(proteome_id: str, out_path: Path) -> None:
    params = {
        "query": f"(proteome:{proteome_id})",
        "format": "fasta",
        "compressed": "false",
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(UNIPROT_STREAM_URL, params=params, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def main():
    proteome_id = "UP000005640"
    fasta_path = Path("proteome.fasta")

    if fasta_path.exists():
        print(f"Using cached {fasta_path.resolve()}")
        return

    print(f"Downloading proteome {proteome_id} -> {fasta_path} ...")
    download_proteome_fasta(proteome_id, fasta_path)
    print("Download complete.")


if __name__ == "__main__":
    main()
