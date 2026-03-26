import os
import argparse
import json
import csv
from pathlib import Path

PROJECT_ROOT = Path(os.environ["PROJECT_ROOT"])
SCRIPT_DIR = Path(os.environ["SCRIPT_DIR"])
YAML_DIR = Path(os.environ["YAML_DIR"])
OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
PROCESSED_DIR = Path(os.environ["PROCESSED_DIR"])

def get_input_file_names(input_folder: str):
    input_loc = YAML_DIR / input_folder

    if not input_loc.exists():
        raise FileNotFoundError(f"Cannot find input directory: {input_loc}")

    file_names = []

    for file_path in input_loc.iterdir():
        if file_path.is_file():
            file_names.append(file_path.name)

    return file_names


def get_predictions_from_input(input_folder: str, file_names: list, batched_outputs: bool = True):
    script_loc = Path(__file__).parent.resolve()

    if batched_outputs:
        output_loc = script_loc.parent / "outputs" / f"boltz_results_{input_folder}"
        # prediction_loc = output_loc / "predictions"
    else:
        output_loc = script_loc.parent / "outputs" / f"{input_folder}"


    confidence_list = []

    for file_name in file_names:

        stem = file_name.split(".")[0]
        

        if batched_outputs:
            pred_folder = output_loc / "predictions" / stem
            confidence_file = pred_folder / f"confidence_{stem}_model_0.json"
        else:
            pred_folder = output_loc / f'boltz_results_{stem}' / "predictions"
            confidence_file = pred_folder / stem / f"confidence_{stem}_model_0.json"


        if not confidence_file.exists():
            print(f"Confidence file not found for {stem}")
            continue

        with open(confidence_file, "r") as f:
            confidence = json.load(f)

        if batched_outputs:
            pred_folder = output_loc / "predictions" / stem
            affinity_file = pred_folder / f"affinity_{stem}.json"
        else:
            pred_folder = output_loc / f'boltz_results_{stem}' / "predictions"
            affinity_file = pred_folder / stem / f"affinity_{stem}.json"



        # affinity_file = pred_folder / f"affinity_{stem}.json"
                    
        if not affinity_file.exists():
            print(f"Affinity file not found for {stem}")
            continue

        with open(affinity_file, "r") as f:
            affinity = json.load(f)

        protein_name = stem.split("__")[0]
        ligand_name = stem.split("__")[1]

        protein_ligand_data = {'protein': protein_name, 'ligand': ligand_name}
        confidence = {**protein_ligand_data, **confidence, **affinity}
        confidence_list.append(confidence)

    # print(confidence_list)
        
    for item in confidence_list:
        affinity_pred_value = item.get("affinity_pred_value", "N/A")
        micromolar_affinity_pred_value = 10 ** affinity_pred_value
        item["micromolar_affinity_pred_value"] = micromolar_affinity_pred_value

    return confidence_list


def get_predictions_from_output(output_folder: Path, verbose: bool = False):
    # output_name = output_folder.name
    confidence_list = []

    num_missing_confidence_files = 0
    num_missing_affinity_files = 0

    for subfolder in output_folder.iterdir():
        stem = subfolder.name.split("boltz_results_")[1]
        
        protein_name = stem.split("__")[0]
        ligand_name = stem.split("__")[1]

        pred_folder = subfolder / "predictions"
        confidence_file = pred_folder / stem / f"confidence_{stem}_model_0.json"

        if not confidence_file.exists():
            if verbose:
                print(f"\tConfidence file not found for {stem}")
            num_missing_confidence_files += 1

        pred_folder = subfolder / "predictions"
        affinity_file = pred_folder / stem / f"affinity_{stem}.json"
      
        if not affinity_file.exists():
            if verbose:
                print(f"\tAffinity file not found for {stem}")
            num_missing_affinity_files += 1

        if not confidence_file.exists() or not affinity_file.exists():
            continue

        with open(confidence_file, "r") as f:
            confidence = json.load(f)

        with open(affinity_file, "r") as f:
            affinity = json.load(f)

        protein_name = stem.split("__")[0]
        ligand_name = stem.split("__")[1]

        protein_ligand_data = {'protein': protein_name, 'ligand': ligand_name}
        confidence = {**protein_ligand_data, **confidence, **affinity}
        confidence_list.append(confidence)
    
    if verbose:
        print(f"\tNumber of missing confidence files: {num_missing_confidence_files}")
        print(f"\tNumber of missing affinity files: {num_missing_affinity_files}")

    for item in confidence_list:
        affinity_pred_value = item.get("affinity_pred_value", "N/A")
        micromolar_affinity_pred_value = 10 ** affinity_pred_value
        item["micromolar_affinity_pred_value"] = micromolar_affinity_pred_value

    return confidence_list


def save_data_as_csv(job_name: str, data: list):
    if not PROCESSED_DIR.exists():
        PROCESSED_DIR.mkdir(parents=True)

    csv_file = PROCESSED_DIR / f"confidence_predictions_{job_name}.csv"

    if not data:
        print(f"No data for {job_name}. Skipping CSV creation.")
        return

    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved confidence predictions to {csv_file.name}")


def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--input_folder", type=str, required=True)
    ap.add_argument("--input_folder", type=str)
    ap.add_argument("--process_all", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    
    if not args.input_folder and not args.process_all:
        print("No arguments provided. Please provide either --input_folder or --process_all.")
        return

    if args.process_all:
        for output_folder in OUTPUT_DIR.iterdir():
            if output_folder.is_dir():
                
                print(f"Processing output folder: {output_folder.name}")
                
                confidence_list = get_predictions_from_output(output_folder, verbose=args.verbose)
                save_data_as_csv(output_folder.name, confidence_list)

    if args.input_folder:
        file_names = get_input_file_names(args.input_folder)
        confidence_list = get_predictions_from_input(args.input_folder, file_names)

        if not confidence_list:
            print(f"No confidence data found for input folder: {args.input_folder}")
            return

        save_data_as_csv(args.input_folder, confidence_list)


if __name__ == "__main__":
    main()
