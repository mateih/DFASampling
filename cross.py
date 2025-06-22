import numpy as np
from sklearn.model_selection import KFold
import os
import sys

# Read the dataset
def load_dataset(filepath):
    examples = []

    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # skip metadata line
            tokens = list(map(int, line.strip().split()))
            if len(tokens) < 2:
                continue
            label = tokens[0]
            length = tokens[1]
            features = tokens[2:2 + length]
            examples.append((label, length, features))

    return examples

# Save dataset to file in the same format
def save_dataset(examples, filepath):
    with open(filepath, 'w') as f:
        f.write(f"{len(examples)} 2\n")
        for label, length, features in examples:
            line = f"{label} {length} " + ' '.join(map(str, features)) + "\n"
            f.write(line)

# Main function
def main():
    # Get filename from command-line or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = 'data.txt'

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    output_dir = 'folds'
    os.makedirs(output_dir, exist_ok=True)

    examples = load_dataset(input_file)
    indices = np.arange(len(examples))
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for i, (train_idx, test_idx) in enumerate(kf.split(indices), start=1):
        train_data = [examples[j] for j in train_idx]
        test_data = [examples[j] for j in test_idx]

        base_name = os.path.splitext(os.path.basename(input_file))[0]
        train_file = os.path.join(output_dir, f"{base_name}_train_fold_{i}.txt")
        test_file = os.path.join(output_dir, f"{base_name}_test_fold_{i}.txt")

        save_dataset(train_data, train_file)
        save_dataset(test_data, test_file)

        print(f"Saved Fold {i}: {train_file}, {test_file}")

if __name__ == "__main__":
    main()
