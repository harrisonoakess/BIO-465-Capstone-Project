import argparse
import json
import csv
from pathlib import Path


def get_input_file_names(input_folder: str):
    script_loc = Path(__file__).parent.resolve()
    input_loc = script_loc.parent / "prep_files/boltz_ready" / input_folder

    if not input_loc.exists():
        raise FileNotFoundError(f"Cannot find input directory: {input_loc}")

    file_names = []

    for file_path in input_loc.iterdir():
        if file_path.is_file():
            file_names.append(file_path.name)

    return file_names


def get_predictions(input_folder: str, file_names: list):
    script_loc = Path(__file__).parent.resolve()
    output_loc = script_loc.parent / "outputs" / f"boltz_results_{input_folder}"
    prediction_loc = output_loc / "predictions"

    confidence_list = []

    for file_name in file_names:
        stem = file_name.split(".")[0]
        
        pred_folder = prediction_loc / stem
        confidence_file = pred_folder / f"confidence_{stem}_model_0.json"

        with open(confidence_file, "r") as f:
            confidence = json.load(f)

        protein_name = stem.split("__")[0]
        ligand_name = stem.split("__")[1]

        protein_ligand_data = {'protein': protein_name, 'ligand': ligand_name}
        confidence = {**protein_ligand_data, **confidence}
        confidence_list.append(confidence)
        
    return confidence_list


def save_data_as_csv(input_folder: str, data: list):
    script_loc = Path(__file__).parent.resolve()
    target_loc = script_loc.parent.resolve() / "processed_data"

    csv_file = target_loc / f"confidence_predictions_{input_folder}.csv"

    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_folder", type=str, required=True)
    # ap.add_argument("--input_folder", type=str, default="paul_tests")
    args = ap.parse_args()

    file_names = get_input_file_names(args.input_folder)
    confidence_list = get_predictions(args.input_folder, file_names)
    save_data_as_csv(args.input_folder, confidence_list)


if __name__ == "__main__":
    main()
