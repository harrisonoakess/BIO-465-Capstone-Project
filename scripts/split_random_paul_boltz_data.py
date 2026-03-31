#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def read_id_set_no_header(csv_path: Path):
    ids = set()

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            value = row[0].strip()
            if value:
                ids.add(value)

    return ids


def split_predictions(
    predictions_csv: Path,
    list_csv: Path,
    output_root: Path,
    prediction_key: str,
) -> None:
    match_ids = read_id_set_no_header(list_csv)

    output_folder = output_root / predictions_csv.stem
    output_folder.mkdir(parents=True, exist_ok=True)

    random_out = output_folder / "random.csv"
    paul_out = output_folder / "paul.csv"

    random_count = 0
    paul_count = 0

    with open(predictions_csv, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError(f"No header found in predictions file: {predictions_csv}")

        if prediction_key not in reader.fieldnames:
            raise ValueError(
                f"Column '{prediction_key}' not found in predictions file.\n"
                f"Found columns: {reader.fieldnames}"
            )

        fieldnames = reader.fieldnames

        with open(random_out, "w", newline="", encoding="utf-8") as random_file, \
             open(paul_out, "w", newline="", encoding="utf-8") as paul_file:

            random_writer = csv.DictWriter(random_file, fieldnames=fieldnames)
            paul_writer = csv.DictWriter(paul_file, fieldnames=fieldnames)

            random_writer.writeheader()
            paul_writer.writeheader()

            for row in reader:
                prediction_value = (row.get(prediction_key) or "").strip()

                if prediction_value in match_ids:
                    random_writer.writerow(row)
                    random_count += 1
                else:
                    paul_writer.writerow(row)
                    paul_count += 1

    print(f"Input predictions file: {predictions_csv}")
    print(f"Input list file:        {list_csv}")
    print(f"Loaded IDs from list:   {len(match_ids)}")
    print(f"Matching '{prediction_key}' against first column of list file")
    print(f"Output folder:          {output_folder}")
    print(f"Random rows written:    {random_count} -> {random_out}")
    print(f"Paul rows written:      {paul_count} -> {paul_out}")


def main():
    parser = argparse.ArgumentParser(
        description="Split prediction CSV rows into random.csv and paul.csv based on membership in a no-header list CSV."
    )
    parser.add_argument("--predictions_csv", required=True)
    parser.add_argument("--list_csv", required=True)
    parser.add_argument("--output_root", default=".")
    parser.add_argument("--prediction_key", default="protein")
    args = parser.parse_args()

    split_predictions(
        predictions_csv=Path(args.predictions_csv),
        list_csv=Path(args.list_csv),
        output_root=Path(args.output_root),
        prediction_key=args.prediction_key,
    )


if __name__ == "__main__":
    main()