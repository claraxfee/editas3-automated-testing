import csv

input_file = "out_deepseek_exception_type.csv"

with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                        project = row.get("project", "").strip()
                                bug_num = row.get("bug_num", "").strip()
                                        full_test_name = row.get("full_test_name", "").strip()
                                                exception_type = row.get("exception_type", "").strip()

                                                        if exception_type == "":
                                                                        exception_type = "<EMPTY>"

                                                                                print(f"Row {i}:")
                                                                                        print(f"Project       : {project}")
                                                                                                print(f"Bug Number    : {bug_num}")
                                                                                                        print(f"Full Test Name: {full_test_name}")
                                                                                                                print(f"Exception     : {exception_type}\n\n")
