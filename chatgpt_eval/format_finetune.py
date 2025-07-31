import csv
import json

input_csv = 'inputs_exceptional_no_split.csv'
output_jsonl = 'output_exceptional.jsonl'

SYSTEM_MESSAGE = (
    "You are an expert Java software developer. You will be given information in the following multiline format:\n"
    "test prefix: <an incomplete unit test prefix>\n"
    "focal method: <the method under test>\n"
    "docstring: <the Java docstring for the method under test>\n"
    "Based on this information, your job is to determine if the developer who wrote the method under test intended "
    "for an exception to occur under the conditions of the prefix. Reply with '1' for yes, '0' for no."
)

with open(input_csv, newline='', encoding='utf-8') as csvfile, open(output_jsonl, 'w', encoding='utf-8') as jsonlfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        label = row['label'].strip()
        test_prefix = row['test'].strip()
        fm = row['fm'].strip()
        docstring = row['docstring'].strip()

        user_content = (
            f"test prefix: {test_prefix}\n"
            f"focal method: {fm}\n"
            f"docstring: {docstring}"
        )

        example = {
            "messages": [
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": label}
            ]
        }

        jsonlfile.write(json.dumps(example) + "\n")

print(f"Done! JSONL fine-tuning data saved to {output_jsonl}")

