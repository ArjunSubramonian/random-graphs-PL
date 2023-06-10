import numpy as np

class MonteCarlo:
    def __init__(self, G, num_samples=1000):
        self.G = G
        self.samples = []
        self.num_samples = num_samples

    def pr(self, stat):
        for _ in range(self.num_samples):
            self.samples.append(self.G.sample(stat))
        values, counts = np.unique(self.samples, return_counts=True)
        dist = counts / self.num_samples
        return dict(zip(values, dist))
