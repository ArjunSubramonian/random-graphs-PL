import numpy as np
from utils import count_triangles
from math import comb


class MonteCarlo:
    def __init__(self, num_samples=1000):
        self.num_samples = num_samples

    def pr(self, G, stat=count_triangles, use_cached=False):
        samples = []
        for _ in range(self.num_samples):
            samples.append(G.sample(stat))
        values, counts = np.unique(samples, return_counts=True)
        dist = counts / self.num_samples
        dist = dict(zip(values, dist))
        dist = {
            t: dist[t] if t in dist else 0.0 for t in range(comb(G.num_nodes, 3) + 1)
        }
        return dist

    def observe_edge(self, G, s, t):
        return G.observe_edge(s, t)

    def observe_no_edge(self, G, s, t):
        return G.observe_no_edge(s, t)

    def observe_triangle(self, G, a, b, c):
        return G.observe_triangle(a, b, c)
