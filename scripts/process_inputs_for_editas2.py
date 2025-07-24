import pandas as pd
import csv
import sys

def process_test_field(test_str, fm_str, docstring_str):
    """
    Process the test field according to the specified rules.
    
    Args:
        test_str (str): Original test string
        fm_str (str): Focal method string
        docstring_str (str): Docstring
        
    Returns:
        str: Processed test string
    """
    # Convert to string and handle potential NaN values
    test_str = str(test_str) if test_str is not None else ""
    fm_str = str(fm_str) if fm_str is not None else ""
    docstring_str = str(docstring_str) if docstring_str is not None else ""
    
    # Step 1: Remove surrounding quotes (only if they exist)
    test_str = test_str.strip()  # Remove any leading/trailing whitespace first
    while test_str.startswith('"') and test_str.endswith('"') and len(test_str) > 1:
        test_str = test_str[1:-1]

    if test_str.startswith('"'):
        test_str = test_str[1:]

    if test_str.endswith('"'):
        test_str = test_str[:-1]
    
    # Step 2: Remove "public" from the beginning if it exists
    if test_str.startswith('public'):
        test_str = test_str[6:].lstrip()  # Remove "public" and any following whitespace
    
    # Step 3: Remove the last instance of "}" from the end
    last_brace_index = test_str.rfind('}')
    if last_brace_index != -1:
        test_str = test_str[:last_brace_index] + test_str[last_brace_index+1:]
    
    # Step 4: Add the hardcoded string exactly as specified
    test_str += ' "<AssertPlaceHolder>" ; }  "<FocalMethod>" '
    

    test_str += fm_str + docstring_str
    
    return test_str

def create_test_id(project, bug_num, full_test_name):
    """
    Create test_id by concatenating project, bug_num, and full_test_name with '::'
    
    Args:
        project (str): Project name
        bug_num: Bug number
        full_test_name (str): Full test name
        
    Returns:
        str: Concatenated test_id
    """
    return f"{project}::{bug_num}::{full_test_name}"

def process_csv(input_file, output_file):
    """
    Process CSV: transform fields and create new output format.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_file}")
        df = pd.read_csv(input_file)
        
        # Display initial statistics
        print(f"Input dataset shape: {df.shape}")
        print(f"Total rows: {len(df)}")
        
        # Check if required columns exist
        required_columns = ['test', 'fm', 'docstring', 'project', 'bug_num', 'full_test_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Process the data to create the new format
        print(f"Processing fields...")
        
        # Create the new dataframe with processed fields
        processed_data = []
        
        for _, row in df.iterrows():
            # Process the test field
            processed_test = process_test_field(
                str(row['test']), 
                str(row['fm']), 
                str(row['docstring'])
            )
            
            # Create test_id
            test_id = create_test_id(
                str(row['project']), 
                str(row['bug_num']), 
                str(row['full_test_name'])
            )
            
            test_id = f'"{test_id}"'
            processed_test = f'"{processed_test}"'

            processed_data.append({
                'processed_test': processed_test,
                'test_id': test_id
            })

        
        # Create new dataframe with both fields
        output_df = pd.DataFrame(processed_data)
        
        # Save full output file (with both fields)
        output_df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONE,escapechar='\\')
        print(f"\nFull processed data saved to: {output_file}")
        print(f"Full output shape: {output_df.shape}")
        
        # Create and save test-only output file (only the processed_test field)
        test_only_df = pd.DataFrame({'processed_test': output_df['processed_test']})
        test_only_file = output_file.replace('.csv', '_test_only.csv')
        test_only_df.to_csv(test_only_file, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
        print(f"Test-only data saved to: {test_only_file}")
        print(f"Test-only output shape: {test_only_df.shape}")
        
        # Show a sample of the output
        print(f"\nSample of processed data:")
        print("=" * 80)
        for i in range(min(2, len(output_df))):
            print(f"Row {i+1}:")
            print(f"  Test ID: {output_df.iloc[i]['test_id']}")
            print(f"  Processed Test (first 100 chars): {output_df.iloc[i]['processed_test'][:100]}...")
            print()
        
        return output_df
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return None
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return None

if __name__ == "__main__":
    # Default file names - modify these as needed
    input_file = "inputs_exceptional_split.csv"  # Change this to your deduplicated file name
    output_file = "processed_inputs_editas2.csv"  # Change this to your desired output file name
    
    # You can also pass file names as command line arguments
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = f"processed_{input_file}"
    
    print("CSV Field Processing Tool")
    print("=" * 40)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("=" * 40)
    
    # Run processing
    result = process_csv(input_file, output_file)
    
    if result is not None:
        print(f"\nProcessing completed successfully!")
        print(f"Generated 2 output files:")
        print(f"  1. Full output with test_id: {output_file}")
        print(f"  2. Test-only output: {output_file.replace('.csv', '_test_only.csv')}")
        print(f"Both files contain {len(result)} processed rows.")
    else:
        print("\nProcessing failed. Please check the error messages above.")
