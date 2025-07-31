import csv
import re

def clean_text(text):
    text = re.sub(r'\btry\b\s*{?', '', text)
    text = re.sub(r'// Undeclared exception!', '', text, flags=re.IGNORECASE)
    text = re.sub(r'fail\s*\([^)]*\)', '', text, flags=re.IGNORECASE)  # remove fail(...)
    text = re.sub(r'catch\s*\([^)]*\)\s*{[^{}]*}', '', text, flags=re.DOTALL)
    # Remove all assertXXX(...) calls, e.g., assertTrue(...), assertEquals(...)
    text = re.sub(r'\bassert\w*\s*\([^)]*\)', '', text, flags=re.IGNORECASE)
    text = re.split(r'["“]?\s*Expecting exception:', text, flags=re.IGNORECASE)[0]
    return text.strip()

with open("inputs_all_no_split.csv", "r", encoding="utf-8", newline='') as infile, \
     open("cleaned_inputs.csv", "w", encoding="utf-8", newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        if len(row) > 1:
            row[1] = clean_text(row[1])
        writer.writerow(row)

