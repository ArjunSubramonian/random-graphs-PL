class ProbabilisticDatabase:
    def __init__(self, G):
        # set up the database and class variables
        self.undirected = G.undirected
        self.db = [(1, [])]
        self.n = G.num_nodes
        # From graph
        # get all of the possible edges with their associated probability (from adjacency list)
        db = [(1, [])]
        edges = []
        for src in G.out_adj_list.keys():
            for tgt, prob in G.out_adj_list[src]:
                # if directed, add every edge
                if not G.undirected:
                    edges.append((src, tgt, prob))
                elif G.undirected and (tgt, src, prob) not in edges:
                    edges.append((src, tgt, prob))

        # populate the database and store the associated probabilties with each world
        for src, tgt, prob in edges:
            world_count = len(self.db)
            for w in range(world_count):
                (prob_og, world) = self.db[w]
                new_world = []
                for src_node, tgt_node in world:
                    new_world.append((src_node, tgt_node))
                new_world.append((src, tgt))
                if G.undirected:
                    new_world.append((tgt, src))
                self.db[w] = (((1 - prob) * prob_og), world)
                self.db.append(((prob * prob_og), new_world))

    def pr(self, G, use_cached=False):
        dist = {}
        for w in range(len(self.db)):
            world_tri_total = 0
            (wp, world) = self.db[w]
            for i in range(self.n):
                # if undirected, just needs to check the one direction
                if self.undirected:
                    for j in range(i, self.n):
                        if (i, j) in world:
                            for k in range(j, self.n):
                                if (i, k) in world and (j, k) in world:
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
        return dict(zip(values, ret_dist))

    def observe_edge(self, G, s, t):
        normalize = 0
        updated_db = []
        for w in range(len(self.db)):
            (wp, world) = self.db[w]
            if ((s, t) in world) or ((t, s) in world):
                normalize += wp
                updated_db.append((wp, world))
        self.db = []
        for wp, world in updated_db:
            self.db.append(((wp / normalize), world))

    def observe_no_edge(self, G, s, t):
        normalize = 0
        updated_db = []
        for w in range(len(self.db)):
            (wp, world) = self.db[w]
            if ((s, t) not in world) and ((t, s) not in world):
                normalize += wp
                updated_db.append((wp, world))
        self.db = []
        for wp, world in updated_db:
            self.db.append(((wp / normalize), world))

    def observe_triangle(self, G, a, b, c):
        if not self.undirected:
            return ValueError(
                "Triangle observations are only supported for undirected graphs."
            )
        self.observe_edge(G, a, b)
        self.observe_edge(G, b, c)
        self.observe_edge(G, a, c)
