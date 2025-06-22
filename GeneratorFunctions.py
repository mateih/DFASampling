import sys
import json
import numpy as np
import random
import copy


### Argument parsing


# The command line arguments. File name is always the first argument. 
# ! These are currently not used !


# arguments: list = sys.argv
# arguments_length: int = len(arguments) # Amount of arguments
# file_name: str = str(input("File/dir name: ") if (arguments_length < 2) else arguments[1])
# accepting_count = input("Amount of accepting samples: ") if (arguments_length < 3) else arguments[2]
# rejecting_count = input("Amount of rejecting samples: ") if (arguments_length < 4) else arguments[3]
# output_file_name: str = str(input("Output file name: ") if (arguments_length < 5) else arguments[4])


### Class Definitions ###

class Edge:
    
    source: int
    target: int
    symbol: int


    def __init__(self, source, target, symbol):
        self.source = source
        self.target = target
        self.symbol = symbol


    # Create the string representation
    def __repr__(self):
        return str(self)
    

    # In the form of "source --symbol-> target"
    def __str__(self):
        return "{} --{}-> {}".format(self.source, self.symbol, self.target)



class Node:

    id: int
    edges: dict[int, Edge]
    accept: bool


    def __init__(self, id, edges, accept = False):
        self.id = id
        self.edges = edges
        self.accept = accept


    # Add/remove edges using +/-
    def __add__(self, other):
        self.edges[other.symbol] = other
        return self
    

    def __sub__(self, other):
        del self.edges[other.symbol]
        return self


    # Create the string representation
    def __repr__(self):
        return str(self)
    

    # The ID, surrounded by () if accepting
    def __str__(self):
        return "({})".format(self.id) if self.accept else str(self.id)



class DFA:
    alphabet: list[int]
    nodes: dict[int, Node]
    edges: list[Edge]
    # Start is assumed to be -1


    def __init__(self, alphabet = [], nodes = {}, edges = []):
        self.alphabet = alphabet
        self.nodes = nodes
        self.edges = edges


    # Handle nodes using list operators (i.e [key] = value)    
    def __getitem__ (self, key) -> Node:
        return self.nodes[key]
    

    def __setitem__ (self, key, value):
        self.nodes[key] = value


    def __delitem__ (self, key):
        del self.nodes[key]
    

    # Add/remove edges using (+/-)
    def __add__ (self, other):
        self.edges.append(other)
        self.nodes[other.source] += other
        return self
    

    def __sub__ (self, other):
        self.edges.remove(other)
        self.nodes[other.source] -= other.target
        return self
    

    # Create the string representation
    def __repr__(self):
        return str(self)


    def __str__ (self):
        return """
            Alphabet: {},
            Nodes: {},
            Edges: {}
            """.format(self.alphabet, list(self.nodes.values()), self.edges)
    

    def simulate(self, word: list[int]) -> bool:
        node_id: int = -1
        node: Node = self.nodes[node_id]
        
        for symbol in word:
            if symbol not in node.edges or node.edges[symbol].target not in self.nodes:
                return False
            
            node = self.nodes[node.edges[symbol].target]

        return node.accept


    def generate(self, alphabet_size, node_count) -> object:

        self.alphabet = list([symbol for symbol in range(alphabet_size)])
        self.nodes.clear()
        self.edges.clear()

        for node_id in range(-1, node_count -1):
            self[node_id] = Node(node_id, {})

        # This decides how many states are accepting. You might want to change this!
        size = int(node_count*0.5)
        positive_node_ids = random.sample(list(self.nodes.keys()), size)
        for node_id in positive_node_ids:
            self[node_id].accept = True

        visited_nodes = [-1]
        unvisited_nodes = list(range(node_count -1))
        while len(unvisited_nodes) > 0:
            source = random.choice(visited_nodes)
            target = random.choice(unvisited_nodes)
            symbol = random.choice(self.alphabet)

            selectable_symbols = list(set(self.alphabet) - set(self[source].edges.keys()))
            if len(selectable_symbols) == 0:
                continue
            symbol = random.choice(selectable_symbols)

            visited_nodes.append(target)
            unvisited_nodes.remove(target)

            edge = Edge(source, target, symbol)
            self += edge
            
        for node_id in range(-1, node_count -1):
           for symbol in list(set(self.alphabet) - set(self[node_id].edges.keys())):
               self += Edge(node_id, random.randint(0, node_count - 1) -1, int(symbol))
        
        return self

    def load_from_file(self, file_name) -> object:
        with open(file_name, 'r') as file:
            data = json.load(file)
            self.alphabet = data["alphabet"]

            for node in data["nodes"]:
                node_id = int(node["id"])
                is_accepting = "final_counts" in node["data"] and "1" in node["data"]["final_counts"] and node["data"]["final_counts"]["1"] > 0
                self[node_id] = Node(node_id, {}, is_accepting)
            
            for edge in data["edges"]:     
                self += Edge(int(edge["source"]), int(edge["target"]), int(edge["name"]))  

        return self    


class TrainingData:

    dfa: DFA
    folds: int
    words: list[list[int]]

    def __init__(self, dfa = None, folds = 0):
        self.dfa = dfa
        self.folds = folds
        self.words = []
    
    def generate_positive(self, total_count) -> object:
        
        self.words.clear()
        max_word_size = 150
        while len(self.words) < total_count:
            
            node: Node = self.dfa.nodes[-1]
            word: list[int] = []
            searching: bool = True
            length: int = 0

            while True:
                # If the state accepts, flip a coin on whether to include that word
                if node.accept and np.random.uniform() <= 1.0 / (1.0 + 2.0 * len(node.edges)):                     
                    self.words.append(copy.copy(word))
                    break

                # If the traversal can't go further, stop and restart
                elif len(node.edges) == 0:
                    break
                
                # Randomly traverse the DFA
                else:
                    random_edge = random.choice(list(node.edges.values()))
                    if random_edge.target not in self.dfa.nodes:
                        break
                    
                    length += 1
                    if length >= max_word_size:
                        break

                    word.append(random_edge.symbol)
                    node = self.dfa.nodes[random_edge.target]
        
        return self

    def generate_negatives(self, negative_count) -> object:

        positive_count = len(self.words)
        for _ in range(negative_count):
            
            word: list[int] = []
            while True:
                
                n = np.random.poisson(3)
                if n == 0:
                    continue
                
                binom = int(np.random.binomial(n, 0.5) - n/2)
                word_len = len(self.words[np.random.randint(0, positive_count)]) + binom
                word_len = max(0, word_len)
                
                word = list([int(random.choice(self.dfa.alphabet)) for _ in range(word_len)])

                if self.dfa.simulate(word) == False:
                    self.words.append(word)
                    break
                
        return self    	

    def split_into_training_and_test_data(self) -> tuple[object, object]:
        self.shuffle()
        split_point = int(len(self.words) * 0.8)

        train_data = TrainingData(self.dfa, 0)
        test_data = TrainingData(self.dfa, 0)

        train_data.words.extend(self.words[:split_point])
        test_data.words.extend(self.words[split_point:])

        return (train_data, test_data)

    def save_to_file(self, file_name):
        with open(file_name, 'w') as file:
            file.write(str(self))

    def shuffle(self):
        np.random.shuffle(self.words)

    # Add/remove edges using (+/-)
    def __add__(self, other):
        for word in other.words:
            self.words.append(word)

        return self

    def __repr__(self):
        return str(self)

    def __str__(self):
        result = ""
        for word in self.words:
            is_accepting = "1" if self.dfa.simulate(word) else "0"
            word_length = len(word)
            result += "\n{} {}".format(is_accepting, word_length)

            for symbol in word:
                result += " " + str(symbol)

        return "{} {}".format(len(self.words), 2) + result


def TestingData():

    size: int
    alphabet_size: int
    accept: list[bool]
    words: list[list[int]]

    def __init__(self, size = 0, alphabet_size = 0):
        self.size = size
        self.alphabet_size = alphabet_size
        self.accept = []
        self.words = []

    def load_from_file(self, file_name) -> object:
        with open(file_name, 'r') as file:
            line = file.read_line().line.split(" ")
            self.size = int(line[0])
            self.alphabet_size = int(line[1])

            for i in range(0, self.size):
                line = file.read_line().line.split(" ")
                self.accept.append(line[0] == "1")
                self.words.append([int(symbol) for symbol in line[2:]])
        
        return self
  

### Insert your own code here! ###
### Or don't! """"

# Code to generate a DFA of your preferred size
alphabet_size = 2

for dfa_size in range(9,14):
    dfa = DFA().generate(alphabet_size, dfa_size)

    # You can combine training and test sets with addition, ie set3 = set1 + set2
    tr = TrainingData(dfa, 1).generate_positive(int(0.75*dfa_size ** 2 )).generate_negatives(int(0.75*dfa_size ** 2))#.split_into_training_and_test_data()

    tr.save_to_file(f"size1/training{dfa_size}_1.txt")
    #te.save_to_file(f"testing/testing{dfa_size}.txt")
