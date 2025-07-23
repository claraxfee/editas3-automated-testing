import pandas as pd

# Load your exceptional.csv
df = pd.read_csv("exceptional.csv")

# Filter to only the tests marked as bug-catching
df = df[df["bug_catching_prefix?"] == 1]

# Build the output DataFrame
out = pd.DataFrame()
out["project"] = df["project"]
out["bug_num"] = df["bug_id"].astype(str)  # important: keep as string
out["test_name"] = df["bug_catching_tests"]
out["bug_type"] = "exception"
out["line_no"] = -1  # Placeholder if you don't know the line
out["error"] = df["exception"]

# Save to bug_catching_tests.csv
out.to_csv("bug_catching_tests.csv", index=False)

