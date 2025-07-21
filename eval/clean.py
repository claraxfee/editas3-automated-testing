import pandas as pd

# Read the CSV file
input_file = 'output.csv' 
output_file = 'good_prefixes.csv'  

# Read the CSV
df = pd.read_csv(input_file)

# Filter rows where 'bug_catching_prefix?' equals 1
filtered_df = df[df['bug_catching_prefix?'] == 1]

# Write the filtered data to a new CSV
filtered_df.to_csv(output_file, index=False)

print(f"Filtered CSV saved to {output_file}")
print(f"Original rows: {len(df)}")
print(f"Filtered rows: {len(filtered_df)}")
