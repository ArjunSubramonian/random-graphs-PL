
# random graph distribution represented using a database
class RandomGraph:
  def __init__(self, num_nodes, prob_adj_list, undirected=True):
    # set up the database and class variables
    self.undirected = undirected
    self.db = [[]]
    self.n = num_nodes
    self.worlds = [1] # probabilities associated with each world

    # get all of the possible edges with their associated probability (from adjacency list)
    edges = []
    for src in prob_adj_list.keys():
      for (tgt,prob) in prob_adj_list[src]:
        # if directed, add every edge
        if not undirected:  
          edges.append((src,tgt,prob))
        # else only add the edge if it is not included
        elif undirected and (tgt,src,prob) not in edges:
          edges.append((src,tgt,prob))

    # populate the database and store the associated probabilties with each world
    for (src,tgt,prob) in edges:
      next_world = len(self.worlds)
      for w in range(len(self.worlds)):
        # get world prob
        wp = self.worlds[w]
        # query the current world
        copy = self.db[w]
        # make a copy of the world 
        for (src_node,tgt_node) in copy:
          if next_world < (len(self.db)):
            self.db[next_world].append((src_node,tgt_node))
          else:
            self.db.append([(src_node,tgt_node)])
        # add the new point to the original world
        self.db[w].append((src,tgt))
        # if undirected, add the other direction too
        if undirected:
          self.db[w].append((tgt,src))
        # update the probabilities
        self.worlds[w] = wp * prob
        self.worlds.append(wp * (1 - prob))
        # move to the next world 
        next_world += 1

# naive counting --> returns the expected value of the number of triangles
def count_triangles(db_graph):
  total = 0
  for w in range(len(db_graph.worlds)):
    world_tri_total = 0
    wp = db_graph.worlds[w] 
    world = db_graph.db[w]
    for i in range(db_graph.n):
      # if undirected, just needs to check the one direction
      if db_graph.undirected:
        for j in range(i,db_graph.n):
          if (i,j) in world:
            for k in range(j,db_graph.n):
              if (i,k) in world and (j,k) in world:
                world_tri_total += 1
    total += (wp * world_tri_total)
  return total # returns the expected value of number of triangles

# Copied over from the prototype.py file to get the probabilities of each edge
p = 0.75
q = 0.25
num_nodes = 7 # Does not scale well

prob_adj_list = { n : [] for n in range(num_nodes)}
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
print(count_triangles(G))