import torch
from torch_geometric.utils import degree
from utils import sp_count_triangles
from math import comb

class MarkovChainMonteCarlo:
    def __init__(self, num_samples=1000):
        self.num_samples = num_samples

    # Algorithm 13 from https://academic.oup.com/book/40058/chapter-abstract/340605713
    def pr(self, G):
        edge_index = G.initial_graph
        N = G.num_nodes
        L = G.num_links
        m = G.deg_dist

        deg = degree(edge_index[0], num_nodes=N)
        sigma = (deg ** 2).sum().item()

        num_triangles = sp_count_triangles(edge_index)
        delta_ij = 0
        delta_ik = 0

        ei = edge_index.clone()

        dist = {}

        for _ in range(self.num_samples):
            if num_triangles not in dist:
                dist[num_triangles] = 0.0
            dist[num_triangles] += 1 / self.num_samples

            while True:
                i, j = ei[:, torch.randint(ei.size(1), (1,))[0]]
                i = i.item()
                j = j.item()
                assert ((ei[0] == j) & (ei[1] == i)).any()

                node_dist = torch.ones(N)
                node_dist[i] = 0
                node_dist[j] = 0
                k = node_dist.multinomial(1)[0]
                k = k.item()

                if (k != ei[1, ei[0] == i]).all():
                    break

            sigma_prime = (sigma + 2 * (1 + deg[k] - deg[j])).item()
            p_execute_move = (
                ((N - 1) * L - sigma)
                * torch.exp(m.log_prob(deg[j] - 1))
                * torch.exp(m.log_prob(deg[k] + 1))
                * (deg[k] + 1)
            )
            p_execute_move /= (
                ((N - 1) * L - sigma_prime)
                * torch.exp(m.log_prob(deg[j]))
                * torch.exp(m.log_prob(deg[k]))
                * deg[j]
            )

            r = torch.rand(1)[0].item()
            if r < p_execute_move.item():
                pos_1 = (ei[0] == i) & (ei[1] == j)
                pos_2 = (ei[0] == j) & (ei[1] == i)
            
                adj_i_1 = ei[1, ei[0] == i]
                adj_j = ei[1, ei[0] == j]

                ei[1, pos_1] = k
                ei[0, pos_2] = k
                
                sigma = sigma_prime

                deg[k] += 1
                deg[j] -= 1

                adj_i_2 = ei[1, ei[0] == i]
                adj_k = ei[1, ei[0] == k]

                delta_ij = -(adj_i_1.reshape(-1, 1) == adj_j).sum()
                delta_ik = (adj_i_2.reshape(-1, 1) == adj_k).sum()
                num_triangles += (delta_ik + delta_ij).item()
        
        dist = {
            t : dist[t] if t in dist else 0.0 for t in range(comb(G.num_nodes, 3) + 1)
        }
        return dist
       
