import os
import re

directory = "."

# Pattern matchers
assert_files = []
prefix_focal_files = []

for filename in os.listdir(directory):
    if re.match(r"\d+_assert\.txt", filename):
        assert_files.append(filename)
    elif re.match(r"\d+_prefix_focal\.txt", filename):
        prefix_focal_files.append(filename)

# Sort files by number prefix
def sort_key(name):
    return int(name.split('_')[0])

assert_files.sort(key=sort_key)
prefix_focal_files.sort(key=sort_key)

# Combine assert files
with open("all_assert.txt", "w") as out_assert:
    for fname in assert_files:
        with open(fname) as f:
            out_assert.write(f.read())

# Combine prefix_focal files
with open("all_prefix_focal.txt", "w") as out_prefix:
    for fname in prefix_focal_files:
        with open(fname) as f:
            out_prefix.write(f.read())

print(f"Combined {len(assert_files)} assert files into all_assert.txt")
print(f"Combined {len(prefix_focal_files)} prefix_focal files into all_prefix_focal.txt")

