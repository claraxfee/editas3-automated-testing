import csv

def evaluate_predictions(csv_file):
    total = 0
    tp = tn = fp = fn = 0

    with open(csv_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row_num, row in enumerate(reader, start=2):  # start=2 for accurate row number in error messages
            try:
                true_label = int(row['label'])
                pred_label = int(row['chatgpt_response'])
            except (ValueError, KeyError):
                print(f"Warning: Skipping row {row_num} due to invalid or missing label values.")
                continue

            total += 1
            if true_label == 1 and pred_label == 1:
                tp += 1
            elif true_label == 0 and pred_label == 0:
                tn += 1
            elif true_label == 0 and pred_label == 1:
                fp += 1
            elif true_label == 1 and pred_label == 0:
                fn += 1

    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    print(f"samples evaluated: {total}")
    print(f"true positives: {tp}")
    print(f"true negatives: {tn}")
    print(f"false positives: {fp}")
    print(f"false negatives: {fn}")
    print(f"\naccuracy:  {accuracy:.4f}")
    print(f"precision: {precision:.4f}")
    print(f"recall:    {recall:.4f}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python accuracy.py <path_to_csv>")
    else:
        evaluate_predictions(sys.argv[1])

