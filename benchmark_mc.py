import numpy as np
import time
import signal
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)

class TimeoutException(Exception):  # Custom exception class
    pass

def timeout_handler(signum, frame):  # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

from mc import MonteCarlo
from random_graph import SampleableRandomGraph
from utils import BA, count_triangles

# num_nodes = 20
# G = SampleableRandomGraph()
# for t in range(num_nodes):
#     G.operate(BA)
# mc = MonteCarlo(G)
# eprint(mc.pr(count_triangles))

print("[")
for num_nodes_step in range(1, 7):
    num_nodes = 2**num_nodes_step
    eprint("num nodes = {}".format(num_nodes))

    times = []
    for p_step in range(1, 6):
        p = 0.2 * p_step
        for q_step in range(1, 6):
            q = 0.2 * q_step
            eprint("p = {}".format(p), "q = {}".format(q))

            signal.alarm(60)  # time out after a minute
            start_time = time.time()
            try:
                prob_adj_list = {n: [] for n in range(num_nodes)}
                for source in range(num_nodes):
                    for target in range(source + 1, num_nodes):
                        if source < num_nodes // 2 and target < num_nodes // 2:
                            prob = p
                        elif source >= num_nodes // 2 and target >= num_nodes // 2:
                            prob = p
                        else:
                            prob = q

                        prob_adj_list[source].append((target, prob))

                G = SampleableRandomGraph(prob_adj_list)
                mc = MonteCarlo(G)
                dist = mc.pr(count_triangles)
            except TimeoutException:
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
        f'{{  "n": {num_nodes}, "mean": {str(np.mean(np.array(times)))}, "std": {str(np.std(np.array(times)))}, "times": {times} }},'
    )
print("]")