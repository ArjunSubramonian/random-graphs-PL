import numpy as np
from numpy.random import binomial, choice


class ExponentialRandomGraph:
    def __init__(self, initial_graph, num_nodes, num_links, deg_dist):
        self.initial_graph = initial_graph
        self.num_nodes = num_nodes
        self.num_links = num_links
        self.deg_dist = deg_dist


class SampleableRandomGraph:
    def __init__(self, out_adj_list=None, undirected=True):
        self.out_adj_list = out_adj_list
        if self.out_adj_list is None:
            # source : (target, prob)
            self.out_adj_list = {0: {1: 1.0}, 1: {}}
        self.num_nodes = len(self.out_adj_list)
        self.undirected = undirected
        self.ops = []

        # executes observations in order
        self.observations = []

    # func : out_adj_list, in_adj_list --> source, probs_list
    def operate(self, func):
        self.ops.append(func)

    def observe_edge(self, s, t):
        self.observations.append(((s, t), 1))

    def observe_no_edge(self, s, t):
        self.observations.append(((s, t), 0))

    def observe_triangle(self, a, b, c):
        if not self.undirected:
            return ValueError(
                "Triangle observations are only supported for undirected graphs."
            )

        self.observe_edge(a, b)
        self.observe_edge(b, c)
        self.observe_edge(a, c)

    def sample(self, stat):
        out_adj_list = {source: set() for source in self.out_adj_list}
        in_adj_list = {source: set() for source in self.out_adj_list}

        # initial independent sampling
        for source in self.out_adj_list:
            for target in self.out_adj_list[source]:
                prob = self.out_adj_list[source][target]
                create_edge = binomial(1, prob) == 1
                if create_edge:
                    out_adj_list[source].add(target)
                    in_adj_list[target].add(source)
                    if self.undirected:
                        out_adj_list[target].add(source)
                        in_adj_list[source].add(target)

        for (s, t), pos in self.observations:
            if pos == 1:
                out_adj_list[s].add(t)
                in_adj_list[t].add(s)
                if self.undirected:
                    out_adj_list[t].add(s)
                    in_adj_list[s].add(t)
            else:
                out_adj_list[s].remove(t)
                in_adj_list[t].remove(s)
                if self.undirected:
                    out_adj_list[t].remove(s)
                    in_adj_list[s].remove(t)

        for op in self.ops:
            source, probs_list = op(out_adj_list, in_adj_list)

            targets = []
            for probs in probs_list:
                targets.append(choice(len(out_adj_list), 1, p=probs)[0])

            if source not in out_adj_list:
                out_adj_list[source] = []
                in_adj_list[source] = []

            for target in targets:
                out_adj_list[source].add(target)
                in_adj_list[target].add(source)
                if self.undirected:
                    out_adj_list[target].add(source)
                    in_adj_list[source].add(target)

        return stat(out_adj_list, in_adj_list)
