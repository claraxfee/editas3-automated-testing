import csv
import re
import argparse
import sys

def process_csv(input_file, output_file):
    pattern = re.compile(r'(.*?</think>)\s*([01])')
    error_count = 0
    row_num = 1  # start from 1 to match line number (assuming header is row 1)

    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        row_num += 1
        if len(header) < 8:
            print("Error: Input CSV must have at least 8 columns.")
            sys.exit(1)

        header[7] = 'label'
        header.append('reasoning')
        writer.writerow(header)

        for row in reader:
            if len(row) < 8:
                print(f"[Row {row_num}] Skipped: Less than 8 fields.")
                row.append('')
                error_count += 1
                writer.writerow(row)
                row_num += 1
                continue

            field = row[7]
            match = pattern.search(field)
            if match:
                reasoning_text = match.group(1)
                label = match.group(2)
                row[7] = label
                row.append(reasoning_text)
            else:
                print(f"[Row {row_num}] Error: Could not parse label from field: '{field}'")
                row.append('')
                error_count += 1

            writer.writerow(row)
            row_num += 1

    print(f"\nTotal rows with errors: {error_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV to extract reasoning and label.")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("--output_csv", default="output.csv", help="Path to output CSV file (default: output.csv)")
    args = parser.parse_args()

    process_csv(args.input_csv, args.output_csv)

