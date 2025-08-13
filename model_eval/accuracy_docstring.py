import csv
import sys

def evaluate_predictions(csv_file):
    """
    Evaluate both original and synthetic docstring predictions against ground truth labels.
    """
    total = 0
    
    # Original docstring metrics
    orig_tp = orig_tn = orig_fp = orig_fn = 0
    
    # Synthetic docstring metrics  
    synth_tp = synth_tn = synth_fp = synth_fn = 0
    
    # Agreement metrics
    agreement_count = 0
    
    with open(csv_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row_num, row in enumerate(reader, start=2):  # start=2 for accurate row number in error messages
            try:
                true_label = int(row['label'])
                orig_pred = int(row['original_chatgpt_response'])
                synth_pred = int(row['synthetic_chatgpt_response'])
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row {row_num} due to invalid or missing values: {e}")
                continue
                
            total += 1
            
            # Evaluate original docstring predictions
            if true_label == 1 and orig_pred == 1:
                orig_tp += 1
            elif true_label == 0 and orig_pred == 0:
                orig_tn += 1
            elif true_label == 0 and orig_pred == 1:
                orig_fp += 1
            elif true_label == 1 and orig_pred == 0:
                orig_fn += 1
                
            # Evaluate synthetic docstring predictions
            if true_label == 1 and synth_pred == 1:
                synth_tp += 1
            elif true_label == 0 and synth_pred == 0:
                synth_tn += 1
            elif true_label == 0 and synth_pred == 1:
                synth_fp += 1
            elif true_label == 1 and synth_pred == 0:
                synth_fn += 1
                
            # Check agreement between original and synthetic
            if orig_pred == synth_pred:
                agreement_count += 1
    
    # Calculate metrics for original docstring
    orig_accuracy = (orig_tp + orig_tn) / total if total > 0 else 0
    orig_precision = orig_tp / (orig_tp + orig_fp) if (orig_tp + orig_fp) > 0 else 0
    orig_recall = orig_tp / (orig_tp + orig_fn) if (orig_tp + orig_fn) > 0 else 0
    orig_f1 = 2 * (orig_precision * orig_recall) / (orig_precision + orig_recall) if (orig_precision + orig_recall) > 0 else 0
    
    # Calculate metrics for synthetic docstring
    synth_accuracy = (synth_tp + synth_tn) / total if total > 0 else 0
    synth_precision = synth_tp / (synth_tp + synth_fp) if (synth_tp + synth_fp) > 0 else 0
    synth_recall = synth_tp / (synth_tp + synth_fn) if (synth_tp + synth_fn) > 0 else 0
    synth_f1 = 2 * (synth_precision * synth_recall) / (synth_precision + synth_recall) if (synth_precision + synth_recall) > 0 else 0
    
    # Calculate agreement rate
    agreement_rate = agreement_count / total if total > 0 else 0
    
    # Print results
    print(f"Total samples evaluated: {total}")
    print(f"Agreement between original and synthetic: {agreement_count}/{total} ({agreement_rate:.4f})")
    print("\n" + "="*60)
    print("ORIGINAL DOCSTRING RESULTS:")
    print("="*60)
    print(f"True positives:  {orig_tp}")
    print(f"True negatives:  {orig_tn}")
    print(f"False positives: {orig_fp}")
    print(f"False negatives: {orig_fn}")
    print(f"\nAccuracy:  {orig_accuracy:.4f}")
    print(f"Precision: {orig_precision:.4f}")
    print(f"Recall:    {orig_recall:.4f}")
    print(f"F1-score:  {orig_f1:.4f}")
    
    print("\n" + "="*60)
    print("SYNTHETIC DOCSTRING RESULTS:")
    print("="*60)
    print(f"True positives:  {synth_tp}")
    print(f"True negatives:  {synth_tn}")
    print(f"False positives: {synth_fp}")
    print(f"False negatives: {synth_fn}")
    print(f"\nAccuracy:  {synth_accuracy:.4f}")
    print(f"Precision: {synth_precision:.4f}")
    print(f"Recall:    {synth_recall:.4f}")
    print(f"F1-score:  {synth_f1:.4f}")
    
    print("\n" + "="*60)
    print("COMPARISON:")
    print("="*60)
    print(f"Accuracy difference:  {synth_accuracy - orig_accuracy:+.4f} (synthetic - original)")
    print(f"Precision difference: {synth_precision - orig_precision:+.4f} (synthetic - original)")
    print(f"Recall difference:    {synth_recall - orig_recall:+.4f} (synthetic - original)")
    print(f"F1-score difference:  {synth_f1 - orig_f1:+.4f} (synthetic - original)")
    
    # Determine which performed better
    if synth_accuracy > orig_accuracy:
        print(f"\n✓ Synthetic docstrings performed BETTER (accuracy: {synth_accuracy:.4f} vs {orig_accuracy:.4f})")
    elif synth_accuracy < orig_accuracy:
        print(f"\n✗ Original docstrings performed BETTER (accuracy: {orig_accuracy:.4f} vs {synth_accuracy:.4f})")
    else:
        print(f"\n= Both performed EQUALLY (accuracy: {orig_accuracy:.4f})")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compare_docstrings.py <path_to_csv>")
        sys.exit(1)
    else:
        evaluate_predictions(sys.argv[1])
