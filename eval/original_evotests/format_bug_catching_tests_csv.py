import csv

input_csv = "bug_catching_tests.csv"     # Replace with your input file path
output_csv = "output.csv"   # Replace with your desired output file path

with open(input_csv, newline='', encoding='utf-8') as infile, \
     open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = ["project", "bug_num", "test_name", "bug_type", "line_no", "error"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    bug_type = "err"
    for row in reader:
        if row["exceptional?"] == "0":
            bug_type = "assertion"
        else:
            bug_type = "exception"

        writer.writerow({
            "project": row["project"],
            "bug_num": row["bug_id"],
            "test_name": row["bug_catching_tests"],
            "bug_type": bug_type,
            "line_no": -1,
            "error": row["exception"]
        })

