import pandas as pd
import sys

def deduplicate_csv(input_file, output_file):
    """
    Deduplicate CSV based on project and bug_num fields, keeping the last occurrence.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_file}")
        df = pd.read_csv(input_file)
        
        # Display initial statistics
        print(f"Original dataset shape: {df.shape}")
        print(f"Total rows: {len(df)}")
        
        # Check if required columns exist
        required_columns = ['project', 'bug_num']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Show duplicate statistics before deduplication
        duplicate_mask = df.duplicated(subset=['project', 'bug_num'], keep=False)
        total_duplicates = duplicate_mask.sum()
        unique_duplicate_groups = df[duplicate_mask].groupby(['project', 'bug_num']).size()
        
        print(f"\nDuplicate analysis:")
        print(f"Total duplicate rows: {total_duplicates}")
        print(f"Number of unique (project, bug_num) groups with duplicates: {len(unique_duplicate_groups)}")
        
        if len(unique_duplicate_groups) > 0:
            print(f"Duplicate group sizes:")
            for (project, bug_num), count in unique_duplicate_groups.items():
                print(f"  {project} bug #{bug_num}: {count} instances")
        
        # Keep only the last occurrence of each (project, bug_num) combination
        # drop_duplicates with keep='last' will keep the last occurrence
        deduplicated_df = df.drop_duplicates(subset=['project', 'bug_num'], keep='last')
        
        # Display final statistics
        print(f"\nAfter deduplication:")
        print(f"Deduplicated dataset shape: {deduplicated_df.shape}")
        print(f"Rows removed: {len(df) - len(deduplicated_df)}")
        print(f"Rows kept: {len(deduplicated_df)}")
        
        # Save to output file
        deduplicated_df.to_csv(output_file, index=False)
        print(f"\nDeduplicated data saved to: {output_file}")
        
        return deduplicated_df
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return None
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return None

if __name__ == "__main__":
    # Default file names - modify these as needed
    input_file = "inputs_exceptional_split.csv"  # Change this to your input file name
    output_file = "deduplicated_output.csv"  # Change this to your desired output file name
    
    # You can also pass file names as command line arguments
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = f"deduplicated_{input_file}"
    
    print("CSV Deduplication Tool")
    print("=" * 50)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("=" * 50)
    
    # Run deduplication
    result = deduplicate_csv(input_file, output_file)
    
    if result is not None:
        print("\nDeduplication completed successfully!")
    else:
        print("\nDeduplication failed. Please check the error messages above.")
