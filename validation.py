import json
import re
import sys
from collections import defaultdict

def load_model(model_file_json: str):
    """Wrapper to load resulting model json file

       Keyword arguments:
       model_file_json -- path to the json model file

       :return: tuple[start_node, dfa as dict, json as dict]
      """
    with open(model_file_json) as fh:
        data = fh.read()

    data = re.sub(r'\"label\" : \"([^\n|])\n([^\n])\"', r'"label" : "\1 \2"', data)

    machine = json.loads(data)

    dfa = defaultdict(lambda: defaultdict(str))

    for edge in machine["edges"]:
        dfa[str(edge["source"])][str(edge["label"])] = str(edge["target"])

    # somtimes in the json of the inferred dfa accepting states are marked 0 and not 1
    if machine['types'][0] == "0":
        is_accepting_1 = True
    else:
        is_accepting_1 = False

    for node in machine["nodes"]:
        if 'final_counts' not in node['data'].keys():
            node_type = '-1'
        elif '0' in node['data']['final_counts'].keys() and node['data']['final_counts']['0'] > 0:
            if is_accepting_1:
                node_type = '0'
            else:
                node_type = '1'
        elif '1' in node['data']['final_counts'].keys() and node['data']['final_counts']['1'] > 0:
            if is_accepting_1:
                node_type = '1'
            else:
                node_type = '0'
        else:
            node_type = '-1'

        dfa[str(node['id'])]["type"] = node_type

    return machine["nodes"][0]["id"], dfa, machine


def traverse(start_node_id, dfa, sequence):
    """Wrapper to traverse a given model with a string

     Keyword arguments:
    - dfa -- loaded model
    - sequence -- space-separated string to accept/reject in dfa
      """

    state = str(start_node_id)
    counter = 0
    if len(sequence) == 0:
        return dfa[state]["type"] == '1'

    for event in sequence.split(" "):
        sym = event.split(":")[0]
        try:
            state = dfa[state][sym]
        except KeyError:
            return False

        counter += 1
        # if state == "":
        #     print("Out of alphabet: non-existent")
        # else:
        #     try:
        #         # take target id, discard counts
        #         state = state[0]
        #     except IndexError:
        #         # print("Out of alphabet: alternatives")
        #         return -1
    return dfa[state]["type"] == '1'


def calculate_accuracy(test_traces, start_node_id, dfa_model):
    """
    Function that calculates the accuracy of an inferred DFA model

    :param test_traces: unseen test traces
    :param start_node_id: id of the start node of the DFA
    :param dfa_model: loaded model
    :return: the following array [#tp, #tn, #fp, #fn, # correct predictions, total number of predictions, bcr accuracy]
    """
    rows = test_traces.split("\n")
    samples = []

    for i in range(len(rows)):
        if i == 0:
            continue
        path = rows[i].split(" ")
        samples.append([" ".join(path[2:]), path[0]])

    counter = 0
    tp = 0;
    tn = 0;
    fp = 0;
    fn = 0
    for sample in samples:
        if sample[1] == '1':
            is_positive = True
        else:
            is_positive = False

        is_accepted = traverse(start_node_id, dfa_model, sample[0])

        if is_accepted == is_positive:
            counter += 1
        if is_accepted:
            if is_positive:
                tp += 1

            else:
                fp += 1
        else:
            if is_positive:
                fn += 1
            else:
                tn += 1
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 1
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 1
    bcr = 2 * sensitivity * specificity / (sensitivity + specificity)
    return [tp, tn, fp, fn, counter, len(samples), bcr]


def evaluate_and_log(dfa_path, test_path, out_file):
    with open(test_path) as f:
        test_data = f.read()

    start_node, dfa_model, _ = load_model(dfa_path)
    metrics = calculate_accuracy(test_data, start_node, dfa_model)

    out_file.write(f"\nModel: {dfa_path}, Test: {test_path}\n")
    #out_file.write("Evaluation Metrics:\n")
    #out_file.write(f"  True Positives:  {metrics[0]}\n")
    #out_file.write(f"  True Negatives:  {metrics[1]}\n")
    #out_file.write(f"  False Positives: {metrics[2]}\n")
    #out_file.write(f"  False Negatives: {metrics[3]}\n")
    #out_file.write(f"  Correct:         {metrics[4]}\n")
    #out_file.write(f"  Total:           {metrics[5]}\n")
    out_file.write(f"  Accuracy:        {metrics[4]/metrics[5]}\n")
    #out_file.write(f"  BCR Accuracy:    {metrics[6]:.4f}\n")


def main():
    with open("trainingresultsrandom50.txt", "a") as out_file:
        for i in range(9,14):
            for j in range(1,6):
                dfa_file = f"size2/random50/training{i}_2_train_fold_{j}.txt.ff.final.json"
                test_file = f"size2/folds/training{i}_2_train_fold_{j}.txt"
                try:
                    evaluate_and_log(dfa_file, test_file, out_file)
                except Exception as e:
                    out_file.write(f"\nError processing model {dfa_file} with test {test_file}: {e}\n")


if __name__ == "__main__":
    main()