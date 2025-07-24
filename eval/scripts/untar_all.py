#!/usr/bin/env python3
import csv
import os
import subprocess
import shutil
from pathlib import Path

def extract_and_organize(csv_file_path, original_evotests_dir):
    """
    Extract .tar.bz2 files based on CSV data and organize them into new folders.
    Uses system tar command to handle bz2 compression.
    
    Args:
        csv_file_path (str): Path to the good_prefixes.csv file
        original_evotests_dir (str): Path to the original_evotests directory
    """
    
    # Ensure the original_evotests directory exists
    if not os.path.exists(original_evotests_dir):
        print(f"Error: Directory {original_evotests_dir} does not exist!")
        return
    
    # Check if tar command is available
    try:
        subprocess.run(['tar', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'tar' command not found. Please make sure tar is installed and available in your PATH.")
        return
    
    # Read the CSV file
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                project = row['project'].strip()
                bug_id = row['bug_id'].strip()
                evosuite_dir = row['evosuite_dir'].strip()
                
                # Construct the path to the .tar.bz2 file
                tar_filename = f"{project}{bug_id}.{evosuite_dir}.tar.bz2"
                tar_path = os.path.join(original_evotests_dir, evosuite_dir, tar_filename)
                
                print(f"Processing: {project}{bug_id} from directory {evosuite_dir}")
                
                # Check if the tar file exists
                if not os.path.exists(tar_path):
                    print(f"  Warning: File {tar_path} not found, skipping...")
                    continue
                
                # Create the destination folder name
                dest_folder = f"{project}{bug_id}_normal"
                
                # Remove destination folder if it already exists
                if os.path.exists(dest_folder):
                    print(f"  Removing existing folder: {dest_folder}")
                    shutil.rmtree(dest_folder)
                
                # Create a temporary extraction directory
                temp_extract_dir = f"temp_extract_{project}{bug_id}"
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir)
                os.makedirs(temp_extract_dir)
                
                try:
                    # Extract the tar.bz2 file using system tar command
                    print(f"  Extracting: {tar_path}")
                    result = subprocess.run([
                        'tar', '-xjf', tar_path, '-C', temp_extract_dir
                    ], capture_output=True, text=True, check=True)
                    
                    # Move extracted contents to the final destination
                    os.rename(temp_extract_dir, dest_folder)
                    print(f"  Created folder: {dest_folder}")
                    
                except subprocess.CalledProcessError as e:
                    print(f"  Error extracting {tar_path}: {e.stderr}")
                    # Clean up temp directory if extraction failed
                    if os.path.exists(temp_extract_dir):
                        shutil.rmtree(temp_extract_dir)
                    continue
                except Exception as e:
                    print(f"  Error processing {tar_path}: {str(e)}")
                    # Clean up temp directory if extraction failed
                    if os.path.exists(temp_extract_dir):
                        shutil.rmtree(temp_extract_dir)
                    continue
    
    except FileNotFoundError:
        print(f"Error: CSV file {csv_file_path} not found!")
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

def main():
    # Set your file paths here
    csv_file = "good_prefixes.csv"
    evotests_dir = "original_evotests"
    
    # Check if files exist before proceeding
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found in current directory!")
        print("Please make sure the file exists or update the csv_file variable.")
        return
    
    if not os.path.exists(evotests_dir):
        print(f"Error: Directory '{evotests_dir}' not found in current directory!")
        print("Please make sure the directory exists or update the evotests_dir variable.")
        return
    
    # Run the extraction and organization
    extract_and_organize(csv_file, evotests_dir)
    print("Processing complete!")

if __name__ == "__main__":
    main()
