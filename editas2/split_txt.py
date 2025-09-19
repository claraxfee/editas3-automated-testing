import csv
import os

input_csv = 'processed_inputs_editas2_test_only.csv'         # change this to your actual input file
output_dir = 'txt'     # folder where .txt files will go

os.makedirs(output_dir, exist_ok=True)

with open(input_csv, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        if not row:
            continue  # skip empty lines
        content = row[0]  # assuming each line is a single long string
        output_path = os.path.join(output_dir, f"{i}.txt")
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(content + '\n')

