#!/usr/bin/env python3
import csv
import sys

def replace_empty_third_field(input_file, output_file=None):
    """
    Replace empty strings in the 3rd field (index 2) with "BLAH"
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file (if None, overwrites input)
    """
    
    # Read all rows first
    rows = []
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                # Check if we have at least 3 fields and if the 3rd field is empty
                if len(row) > 2 and row[2] == "":
                    row[2] = "BLAH"
                rows.append(row)
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found!")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Write back to file
    output_path = output_file if output_file else input_file
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"Successfully processed {len(rows)} rows.")
        if output_file:
            print(f"Output written to: {output_file}")
        else:
            print(f"File '{input_file}' updated in place.")
        return True
            
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py input.csv [output.csv]")
        print("If output.csv is not specified, input.csv will be modified in place.")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    replace_empty_third_field(input_file, output_file)

if __name__ == "__main__":
    main()
