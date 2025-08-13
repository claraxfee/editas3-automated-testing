import csv
from pprint import pprint

input_file = "wrong.csv"

fourth_fields = []

with open(input_file, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)  # skip header
    for i, row in enumerate(reader, start=1):
        field = row[3].strip() if len(row) > 3 else ""
        if field == "":
            display_field = "<EMPTY>"
        else:
            display_field = field
        fourth_fields.append(display_field)

# Pretty print each field with two newlines in between
for i, field in enumerate(fourth_fields, start=1):
    print(f"Row {i}: {field}\n\n")

# Summary
total_rows = len(fourth_fields)
empty_count = sum(1 for f in fourth_fields if f == "<EMPTY>")
print(f"Total rows: {total_rows}")
print(f"Empty 4th fields: {empty_count}")

