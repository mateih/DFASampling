import random
import Levenshtein
from collections import defaultdict

def read_traces(filename):
    with open(filename, 'r') as f:
        n, m = map(int, f.readline().split())
        traces = []
        for _ in range(n):
            parts = f.readline().split()
            label = int(parts[0])
            length = int(parts[1])
            trace = ''.join(parts[2:])
            traces.append((label, length, trace))
        return traces, m

def write_traces(filename, traces, alphabet_size):
    with open(filename, 'w') as f:
        f.write(f"{len(traces)} {alphabet_size}\n")
        for label, length, trace in traces:
            f.write(f"{label} {length} {' '.join(trace)}\n")

def group_by_suffix(traces, k):
    groups = defaultdict(list)
    for label, length, trace in traces:
        key = trace[-k:] if k <= len(trace) else trace
        groups[(label, key)].append((label, length, trace))
    return groups

def sample_diverse_traces(trace_tuples, num_samples=5):
    traces = [trace for _, _, trace in trace_tuples]
    if len(traces) <= num_samples:
        return trace_tuples
    scores = []
    for i, t1 in enumerate(traces):
        min_dist = min(
            Levenshtein.distance(t1, t2)
            for j, t2 in enumerate(traces) if i != j
        )
        scores.append((min_dist, trace_tuples[i]))
    scores.sort(reverse=True)
    return [tup for _, tup in scores[:num_samples]]

def dynamic_k_sampling(traces, target_samples, initial_k=2):
    sampled = []
    k = initial_k
    while len(sampled) < target_samples:
        groups = group_by_suffix(traces, k)
        traces_per_group = max(1, (target_samples - len(sampled)) // len(groups))
        for group in groups.values():
            sampled.extend(random.sample(group, min(len(group), traces_per_group)))
            if len(sampled) >= target_samples:
                break
        k += 1
    return sampled[:target_samples]

def binary_search_k(traces, target_samples):
    low, high = 1, max(int(len(trace)/2) for _, _, trace in traces)
    target_groups = max(1, target_samples // 5)

    def num_groups(k):
        return len(group_by_suffix(traces, k)) #len(group_by_suffix(traces, mid))

    while low < high:
        mid = (low + high) // 2
        if num_groups(mid) > target_groups:
            high = mid - 1
        else:
            low = mid +1
    return low


def sample_with_binary_search(traces, target_samples):
    k = binary_search_k(traces, target_samples)
    groups = group_by_suffix(traces, k)

    sampled = []
    group_representatives = []

    # Step 1: Ensure one representative per group
    group_values = list(groups.values())
    random.shuffle(group_values)
    for group in group_values:
        representative = random.choice(group)
        group_representatives.append(representative)

    sampled.extend(group_representatives)

    # Step 2: If more samples are needed, fill in with diverse traces from groups
    remaining_samples = target_samples - len(sampled)
    if remaining_samples > 0:
        extra = []
        for group in groups.values():
            if len(group) > 1:
                # Exclude the already chosen representative
                group_others = [x for x in group if x not in sampled]
                extra.extend(sample_diverse_traces(group_others, num_samples=5))
        ##random.shuffle(extra)
        sampled.extend(extra[:remaining_samples])

    return sampled[:target_samples]


def random_sampling(traces, target_samples):
    return random.sample(traces, min(len(traces), target_samples))

def run_sampling():

    for percent in [25, 50]:
        for i in range(5, 21):
            input_file = f"training/training{i}.txt"
            output_file = f"training/random/training{i}random{percent}.txt"

            try:
                traces, alphabet_size = read_traces(input_file)
                total_traces = len(traces)
                target_samples = max(1, int(total_traces * percent / 100))

                print(f"Sampling {target_samples} traces from {input_file} ({percent}%) using random method...")

                sampled = random_sampling(traces, target_samples)
                write_traces(output_file, sampled, alphabet_size)

                print(f"  → Sampled traces written to {output_file}")

            except Exception as e:
                print(f"Error processing {input_file} with {percent}% dynamic sampling: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Input file')
    parser.add_argument('--percent', type=float, required=True, help='Percent of traces to sample (e.g., 10 for 10%)')
    parser.add_argument('--method', choices=['dynamic', 'binary', 'random'], default='binary', help='Sampling method')
    parser.add_argument('--output', required=True, help='Output file')
    args = parser.parse_args()

    traces, alphabet_size = read_traces(args.file)
    total_traces = len(traces)
    target_samples = max(1, int(total_traces * args.percent / 100))

    #print(f"Sampling {target_samples} traces out of {total_traces} ({args.percent}%) using {args.method} method...")

    if args.method == 'dynamic':
        sampled = dynamic_k_sampling(traces, target_samples)
    elif args.method == 'binary':
        sampled = sample_with_binary_search(traces, target_samples)
    else:  # 'random'
        sampled = random_sampling(traces, target_samples)

    write_traces(args.output, sampled, alphabet_size)
    #print(f"Sampled traces written to: {args.output}")

if __name__ == '__main__':
    main()
