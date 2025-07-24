#!/usr/bin/env python3
import csv
import sys

def update_labels(inputs_file, good_prefixes_file, output_file=None):
    """
    Update labels in inputs_normal.csv based on matching project/bug_num with good_prefixes.csv
    
    Args:
        inputs_file (str): Path to inputs_normal.csv
        good_prefixes_file (str): Path to good_prefixes.csv  
        output_file (str): Path to output file (if None, overwrites inputs_file)
    """
    
    # First, read good_prefixes.csv and create a lookup dictionary
    lookup = {}
    
    try:
        with open(good_prefixes_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                project = row['project'].strip()
                bug_id = row['bug_id'].strip()
                exceptional = row['exceptional?'].strip()
                
                # Create key as (project, bug_id) tuple
                key = (project, bug_id)
                lookup[key] = exceptional
                
        print(f"Loaded {len(lookup)} entries from {good_prefixes_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{good_prefixes_file}' not found!")
        return False
    except Exception as e:
        print(f"Error reading {good_prefixes_file}: {e}")
        return False
    
    # Now read inputs_normal.csv and update labels
    updated_rows = []
    matches_found = 0
    no_match_count = 0
    
    try:
        with open(inputs_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                project = row['project'].strip()
                bug_num = row['bug_num'].strip()
                
                # Look up the exceptional value
                key = (project, bug_num)
                if key in lookup:
                    old_label = row['label']
                    row['label'] = lookup[key]
                    matches_found += 1
                    if old_label != row['label']:
                        print(f"Updated {project}{bug_num}: '{old_label}' -> '{row['label']}'")
                else:
                    print(f"Warning: No match found for {project}{bug_num}")
                    no_match_count += 1
                
                updated_rows.append(row)
        
        print(f"Processed {len(updated_rows)} rows from {inputs_file}")
        print(f"Found matches for {matches_found} rows")
        print(f"No matches found for {no_match_count} rows")
        
    except FileNotFoundError:
        print(f"Error: File '{inputs_file}' not found!")
        return False
    except Exception as e:
        print(f"Error reading {inputs_file}: {e}")
        return False
    
    # Write the updated data
    output_path = output_file if output_file else inputs_file
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        if output_file:
            print(f"Updated data written to: {output_file}")
        else:
            print(f"File '{inputs_file}' updated in place.")
        return True
            
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py inputs_normal.csv good_prefixes.csv [output.csv]")
        print("If output.csv is not specified, inputs_normal.csv will be modified in place.")
        return
    
    inputs_file = sys.argv[1]
    good_prefixes_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    update_labels(inputs_file, good_prefixes_file, output_file)

if __name__ == "__main__":
    main()
