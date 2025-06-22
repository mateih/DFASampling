import sys
import random


def read_trace_file(filename):
    with open(filename, 'r') as f:
        lines = f.read().strip().splitlines()

    num_traces, alphabet_size = map(int, lines[0].split())
    traces = []

    for line in lines[1:]:
        parts = list(map(int, line.strip().split()))
        label = parts[0]
        length = parts[1]
        sequence = tuple(parts[2:])
        traces.append((label, length, sequence))

    return alphabet_size, traces


def write_trace_file(filename, alphabet_size, traces):
    with open(filename, 'w') as f:
        f.write(f"{len(traces)} {alphabet_size}\n")
        for label, length, sequence in traces:
            trace_str = ' '.join(map(str, sequence))
            f.write(f"{label} {length} {trace_str}\n")


def process_trace_file(input_file, output_file1, output_file2):
    alphabet_size, traces = read_trace_file(input_file)

    # Remove duplicates
    unique_traces = list(set(traces))

    # Shuffle for randomness
    random.shuffle(unique_traces)

    # Split into two equal parts
    mid = len(unique_traces) // 2
    split1 = unique_traces[:mid]
    split2 = unique_traces[mid:]

    # Write output files
    write_trace_file(output_file1, alphabet_size, split1)
    write_trace_file(output_file2, alphabet_size, split2)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python split_traces.py input.txt output1.txt output2.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file1 = sys.argv[2]
    output_file2 = sys.argv[3]

    process_trace_file(input_file, output_file1, output_file2)
