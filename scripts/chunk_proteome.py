from pathlib import Path 

fasta_file = Path("../prep_files/output_files/proteome.fasta")
out_dir = Path("/scratch/rai/vast1/stewartp/proteome_chunks")
out_dir.mkdir(parents=True, exist_ok=True)

chunk_size = 1
seqs = []
counter = 0

with open(fasta_file) as f:
    seq = []
    for line in f:
        if line.startswith(">"):
            if seq:
                # Save previous sequence
                out_file = out_dir / f"seq_{counter:03d}.fasta"
                with open(out_file, "w") as out:
                    out.writelines(seq)
                counter += 1
                seq = []
        seq.append(line)
    if seq:
        out_file = out_dir / f"seq_{counter:03d}.fasta"
        with open(out_file, "w") as out:
            out.writelines(seq)