import numpy as np
from numpy.random import binomial, choice
import itertools
import time

import signal

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

class RandomGraph:
  def __init__(self, num_nodes, prob_adj_list, undirected=True):
    # set up the database and class variables
    self.undirected = undirected
    self.db = [(1,[])]
    self.n = num_nodes

    # get all of the possible edges with their associated probability (from adjacency list)
    edges = []
    for src in prob_adj_list.keys():
      for (tgt,prob) in prob_adj_list[src]:
        # if directed, add every edge
        if not undirected:  
          edges.append((src,tgt,prob))
        elif undirected and (tgt,src,prob) not in edges:
          edges.append((src,tgt,prob))

    # populate the database and store the associated probabilties with each world
    for (src,tgt,prob) in edges:
      world_count = len(self.db)
      for w in range(world_count):
        (prob_og,world) = self.db[w]
        new_world = []
        for (src_node,tgt_node) in world:
          new_world.append((src_node,tgt_node))
        new_world.append((src,tgt))
        if undirected:
          new_world.append((tgt,src))
        self.db[w] = (((1-prob) * prob_og),world)
        self.db.append(((prob * prob_og),new_world))

# naive counting --> returns the expected value of the number of triangles
def count_triangles(db_graph):
    dist = {}
    for w in range(len(db_graph.db)):
        world_tri_total = 0 
        (wp,world) = db_graph.db[w]
        for i in range(db_graph.n):
        # if undirected, just needs to check the one direction
            if db_graph.undirected:
                for j in range(i,db_graph.n):
                    if (i,j) in world:
                        for k in range(j,db_graph.n):
                            if (i,k) in world and (j,k) in world:
                                world_tri_total += 1
        triangle_key = f"{world_tri_total}"
        if triangle_key in dist.keys():
            dist[triangle_key] = dist[triangle_key] + wp
        else:
            dist[triangle_key] = wp
    values = []
    ret_dist = []
    for key in dist.keys():
       values.append(int(key))
       ret_dist.append(dist[key])
    return values,ret_dist # returns the expected value of number of triangles


########################## Testing Loops (reusing from mc.py) ###########################
for num_nodes_step in range(1, 16):
    num_nodes = 2 ** num_nodes_step
    print('num nodes = {}'.format(num_nodes))

    times = []
    for p_step in range(1, 6):
        p = 0.2 * p_step
        for q_step in range(1, 6):
            q = 0.2 * q_step
            print('p = {}'.format(p), 'q = {}'.format(q))

            signal.alarm(60)  # time out after a minute
            start_time = time.time()
            try:
                prob_adj_list = {
                    n : [] for n in range(num_nodes)
                }
                for source in range(num_nodes):
                    for target in range(source + 1, num_nodes):
                        if source < num_nodes // 2 and target < num_nodes // 2:
                            prob = p
                        elif source >= num_nodes // 2 and target >= num_nodes // 2:
                            prob = p
                        else:
                            prob = q

                        prob_adj_list[source].append((target, prob))

                G = RandomGraph(num_nodes,prob_adj_list)
                values, dist = count_triangles(G)
                print(np.dot(values, dist))
            except TimeoutException:
                pass
            else:
                # Reset the alarm
                signal.alarm(0)

            time_elapsed = time.time() - start_time
            times.append(time_elapsed)

    print()
    print("time taken:", str(np.mean(np.array(times))) + " ± " + str(np.std(np.array(times))))
    print()