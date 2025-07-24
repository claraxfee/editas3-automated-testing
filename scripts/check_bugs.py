#!/usr/bin/env python3
import csv

def check_bugs():
    # Read all lines from inputs.csv and create a set of project,bug combinations
    inputs_bugs = set()
    with open('inputs.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            bug_id = f"{row[4]},{row[5]}"
            inputs_bugs.add(bug_id)
    
    # Check each bug from bug_catching_tests.csv
    with open('bug_catching_tests.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            bug_id = f"{row[0]},{row[1]}"
            if bug_id not in inputs_bugs:
                print(f"{bug_id} is missing from inputs.csv")

if __name__ == "__main__":
    check_bugs()
