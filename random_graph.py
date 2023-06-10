import numpy as np
from numpy.random import binomial, choice

class SampleableRandomGraph:
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

        return stat(out_adj_list, in_adj_list)