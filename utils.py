import itertools
import torch
from torch_geometric.utils import to_torch_coo_tensor

# assumes graph is directed
def BA(out_adj_list, in_adj_list, m=2):
    in_degs = [len(in_adj_list[target]) for target in in_adj_list]
    Z = sum(in_degs)
    probs = [d / Z for d in in_degs]
    return len(in_degs), [probs for _ in range(m)]

# assumes graph is undirected
def count_triangles(out_adj_list, in_adj_list):
    num_nodes = len(out_adj_list)
    num_triangles = 0
    for subset in itertools.combinations(list(range(num_nodes)), 3):
        n1, n2, n3 = subset
        if n2 in out_adj_list[n1] and n3 in out_adj_list[n2] and n1 in out_adj_list[n3]:
            num_triangles += 1
    return num_triangles

# assumes graph is undirected
def sp_count_triangles(edge_index):
    sp_edge_index = to_torch_coo_tensor(edge_index)
    mp = torch.sparse.mm(torch.sparse.mm(sp_edge_index, sp_edge_index), sp_edge_index)
    idx = mp.indices()
    vals = mp.values()

    mask = idx[0] == idx[1]
    return vals[mask].sum().item() / 6
