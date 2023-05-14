import numpy as np
from numpy.random import binomial, choice

class RandomGraph:
    def __init__(self, out_adj_list=None, undirected=True):
        self.out_adj_list = out_adj_list
        if self.out_adj_list is None:
            # source : (target, prob)
            self.out_adj_list = {
                0 : [(1, 1.0)],
                1 : []
            }
        self.undirected = undirected
        self.ops = []
        self.samples = []
    
    # func : out_adj_list, in_adj_list --> source, probs_list
    def operate(self, func):
        self.ops.append(func)

    def sample(self, stat):
        out_adj_list = {
            source : [] for source in self.out_adj_list
        }
        in_adj_list = {
            source : [] for source in self.out_adj_list
        }
        # initial independent sampling
        for source in self.out_adj_list:
            for (target, prob) in self.out_adj_list[source]:
                create_edge = binomial(1, prob) == 1
                if create_edge:
                    out_adj_list[source].append(target)
                    in_adj_list[target].append(source)
                    if self.undirected:
                        out_adj_list[target].append(source)
                        in_adj_list[source].append(target)

        for op in self.ops:
            source, probs_list = op(out_adj_list, in_adj_list)

            targets = []
            for probs in probs_list:
                targets.append(choice(len(out_adj_list), 1, p=probs)[0])
            
            for target in targets:
                if source not in out_adj_list:
                    out_adj_list[source] = []
                    in_adj_list[source] = []
                out_adj_list[source].append(target)
                in_adj_list[target].append(source)
                if self.undirected:
                    out_adj_list[target].append(source)
                    in_adj_list[source].append(target)

        self.samples.append(stat(out_adj_list, in_adj_list))

def BA(out_adj_list, in_adj_list, m=2):
    in_degs = [len(in_adj_list[target]) for target in in_adj_list]
    Z = sum(in_degs)
    probs = [d / Z for d in in_degs]
    return len(in_degs), [probs for _ in range(m)]

def count_triangles(out_adj_list, in_adj_list):
    num_triangles = 0
    for n1 in out_adj_list:
        for n2 in out_adj_list[n1]:
            for n3 in out_adj_list[n2]:
                num_triangles += int(n1 in out_adj_list[n3])
    return num_triangles

def pr(G, stat, n=1000):
    for _ in range(n):
        G.sample(stat)
    values, counts = np.unique(G.samples, return_counts=True)
    dist = counts / np.sum(counts)
    return (values, dist)

num_nodes = 100
G = RandomGraph()
for t in range(num_nodes):
    G.operate(BA)
print(pr(G, count_triangles))

p = 0.5
prob_adj_list = {
    n : [] for n in range(num_nodes)
}
for source in range(num_nodes):
    for target in range(source + 1, num_nodes):
        prob_adj_list[source].append((target, p))
G = RandomGraph(prob_adj_list)
print(pr(G, count_triangles))