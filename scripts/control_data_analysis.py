import argparse
import json
import csv
from pathlib import Path
import pandas as pd

from output_parsing_to_csv import get_input_file_names, get_predictions, save_data_as_csv

ref_file_path = Path(__file__).parent.parent.resolve() / "prep_files" / "output_files" / "control_proteins.csv"
control_output_path = Path(__file__).parent.resolve() / "control_outputs"

def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--input_folder", type=str, required=True)
    ap.add_argument("--input_folder", type=str, default="control_tests")
    args = ap.parse_args()

    reference_data = pd.read_csv(ref_file_path)
    file_names = get_input_file_names(args.input_folder)

    confidence_list = get_predictions(args.input_folder, file_names)
    save_data_as_csv(args.input_folder, confidence_list)


if __name__ == "__main__":
    main()
