import pandas as pd

# Load wrong.csv
df = pd.read_csv("wrong.csv")

for _, row in df.iterrows():
    print(f"{row['project']} {row['bug_num']}")
    print(f"Actual label: {row['label']}")
    print(f"Predicted label: {row['chatgpt_response']}\n")
   
    print(f"Test path: {row['full_test_name']}\n")

    print(f"Test prefix: {row['test']}\n")
    print(f"Focal method: {row['fm']}\n")
    print(f"Docstring: {row['docstring']}\n")
    
    input("Press Enter to see the next one...")
    print("-" * 60)

