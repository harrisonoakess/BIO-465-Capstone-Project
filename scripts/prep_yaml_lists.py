import os
from pathlib import Path
import argparse

YAML_DIR = Path(os.environ["YAML_DIR"])
OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
YAML_LIST_DIR = Path(os.environ["YAML_LIST_DIR"])

def get_list_finished_yaml_files(output_folder: Path):
    # Look in output directory for YAML files with completed predictions
    # Return list of finished YAML files and list of unfinished YAML files
    
    finished_yaml_files = []

    for yaml_folder in output_folder.iterdir():
        name = yaml_folder.name.split("boltz_results_")[-1]
        pred_folder = yaml_folder / "predictions" / name
        yaml_file_name = f"{name}.yaml"

        yaml_file_path = YAML_DIR / output_folder.name / yaml_file_name

        if prediction_successful(pred_folder):
            finished_yaml_files.append(yaml_file_path)
       
    return finished_yaml_files


def prediction_successful(pred_folder: Path):
    # Check if prediction folder contains confidence and affinity files

    confidence_file = pred_folder / f"confidence_{pred_folder.name}_model_0.json"
    affinity_file = pred_folder / f"affinity_{pred_folder.name}.json"

    if not confidence_file.exists() or not affinity_file.exists():
        return False
    else:
        return True


def process_output_folder(output_folder: Path, verbose: bool = False):
    # Get list of finished YAML files

    folder_name = output_folder.name

    if not output_folder.is_dir():
        raise NotADirectoryError(f"Error: Output folder '{folder_name}' is not a valid directory.")
        
    elif not output_folder.exists():
        raise FileNotFoundError(f"Error: Output folder '{folder_name}' does not exist.")

    # print(f"Checking output folder '{folder_name}' for completed predictions...")

    finished_yaml_files = get_list_finished_yaml_files(output_folder)

    job_name = folder_name.split("boltz_results_")[-1]
    input_yaml_files = get_input_yaml_files(job_name)

    if verbose:
        report = f"Prediction Status {folder_name}:"
        report += f"\n\tFinished: {len(finished_yaml_files)}"
        report += f"\tUnfinished: {len(input_yaml_files) - len(finished_yaml_files)}"
        report += f"\tTotal: {len(input_yaml_files)}"
        report += f"\tPercentage: {len(finished_yaml_files) / len(input_yaml_files) * 100:.2f}%"
        print(report)

    return finished_yaml_files, input_yaml_files


def create_yaml_list(finished_yaml_files: list, input_yaml_files: list, output_folder_name: str):
    # Make a list of YAML files which have not been successfully processed by Boltz
    
    if len(finished_yaml_files) == len(input_yaml_files):
        print(f"All YAML files in {output_folder_name} have been processed successfully. No list will be created.")
        return

    if len(finished_yaml_files) == 0:
        print(f"No YAML files in {output_folder_name} have been processed successfully. List of all input YAML files will be used.")
    
    list_file_name = f"yaml_list_{output_folder_name}.txt"
    yaml_list_location = YAML_LIST_DIR / list_file_name

    unfinished_yaml_files = []

    for yaml_file in input_yaml_files:
        if yaml_file not in finished_yaml_files:
            unfinished_yaml_files.append(yaml_file)

    with open(yaml_list_location, "w") as f:
        for yaml_file in unfinished_yaml_files:
            f.write(f"{yaml_file}\n")


def get_input_yaml_files(input_folder: str):
    input_folder_path = YAML_DIR / input_folder
    yaml_files = []

    for file in input_folder_path.iterdir():
        if file.is_file() and file.suffix == ".yaml":
            yaml_files.append(file)

    return yaml_files


def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--input_folder", type=str, required=True)
    ap.add_argument("--output_folder", type=str, nargs="+")
    ap.add_argument("--process_all", action="store_true")
    # ap.add_argument("--process_all", action="store_true", default=True)
    ap.add_argument("--create_list", action="store_true", help="Create list of unfinished YAML files for supplemental predictions")
    # ap.add_argument("--create_list", action="store_true", default=True)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not args.output_folder and not args.process_all:
        print("No arguments provided. Please provide either --output_folder or --process_all.")
        return

    folders = []

    if args.process_all:
        print("Processing all output folders...")
        for folder_path in OUTPUT_DIR.iterdir():
            if folder_path.is_dir():
                folders.append(folder_path)
    elif args.output_folder:
        for folder_name in args.output_folder:
            folder_path = OUTPUT_DIR / folder_name
            if folder_path.is_dir():
                folders.append(folder_path)
            else:
                print(f"Warning: Output folder '{folder_name}' is not a valid directory and will be skipped.")
        
    for folder_path in folders:
        finished_yaml_files, input_yaml_files = process_output_folder(folder_path, verbose=args.verbose)
        if args.create_list:
            create_yaml_list(finished_yaml_files, input_yaml_files, folder_path.name)


if __name__ == "__main__":
    main()
