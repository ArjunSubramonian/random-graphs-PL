import torch
from torch.distributions.categorical import Categorical
from torch_geometric.utils import coalesce, remove_self_loops
import numpy as np

from random_graph import ExponentialRandomGraph
from mcmc import MarkovChainMonteCarlo

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

import time
import signal

class TimeoutException(Exception):  # Custom exception class
    pass

def timeout_handler(signum, frame):  # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

print("[")

for num_nodes_step in range(2, 10):
    N = 2**num_nodes_step
    eprint("num nodes = {}".format(N))

    times = []
    for p_step in range(2, 11):
        p = 0.1 * p_step
        L = int(p * N * N)

        eprint("number of links = {}".format(L))

        signal.alarm(60)  # time out after a minute
        start_time = time.time()

        try:
            m = Categorical(torch.ones(N) / N)

            perm = torch.randperm(N * N)
            idx = perm[: L // 2]
            edge_index = torch.zeros((2, L)).long()
            for pos, i in enumerate(idx):
                u = i // N
                v = i % N
                edge_index[0, 2 * pos] = u
                edge_index[1, 2 * pos] = v
                edge_index[0, 2 * pos + 1] = v
                edge_index[1, 2 * pos + 1] = u

            edge_index = coalesce(edge_index)
            edge_index, _ = remove_self_loops(edge_index)
           
            G = ExponentialRandomGraph(edge_index, N, L, m)
            mcmc = MarkovChainMonteCarlo()
            dist = mcmc.pr(G)

        except TimeoutException:
            eprint("Took too long!")
            pass
        else:
            # Reset the alarm
            signal.alarm(0)

        time_elapsed = time.time() - start_time
        times.append(time_elapsed)

    eprint()
    eprint(
        "time taken:",
        str(np.mean(np.array(times))) + " ± " + str(np.std(np.array(times))),
    )
    eprint()

    print(
        f'{{  "n": {N}, "mean": {str(np.mean(np.array(times)))}, "std": {str(np.std(np.array(times)))}, "times": {times} }},'
    )
print("]")