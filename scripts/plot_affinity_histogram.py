import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to input CSV")
    parser.add_argument("--output", default="affinity_histogram.png", help="Output plot filename")
    parser.add_argument("--bins", type=int, default=30, help="Number of histogram bins")
    parser.add_argument("--log", action="store_true", help="Use log scale on x-axis")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.csv)

    affinity_col = "micromolar_affinity_pred_value"

    if affinity_col not in df.columns:
        raise ValueError(f"Column '{affinity_col}' not found in CSV")

    data = df[affinity_col].dropna()

    output = os.path.join("/uufs/chpc.utah.edu/common/home/u6073678/Capstone/BIO-465-Capstone-Project/plots", args.output)

    # Plot
    plt.figure(figsize=(10, 6))

    plt.hist(data, bins=args.bins, edgecolor="black")

    plt.title("Distribution of Predicted CER_d18_0_16_0_C16 Binding Affinities")
    plt.xlabel("Affinity (micromolar, lower = stronger binding)")
    plt.ylabel("Frequency")

    if args.log:
        plt.xscale("log")

    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()

    print(f"Saved histogram to {output}")


if __name__ == "__main__":
    main()