"""
Module for experimenting with logical formula compilation of clique-counting. Broadly, we generate a DNF representing triangle counting (for an arbitrary graph), perform a Tseitin transform to convert it to a CNF, and then output it in DIMACS form.
"""

from argparse import ArgumentParser, BooleanOptionalAction
import sys
import time
import numpy as np
from math import comb

# only for bench
from pysdd.sdd import SddManager, Vtree, WmcManager


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Propositional:
    """
    Weighted model count solver for triangle counting.
    Currently doesn't work! I've pushed a version that enumerates the approach we tried.
    """

    def __init__(self, G):
        self.clauses = triangle_cnf(G.num_nodes)
        self.weights = []
        # idea: initialize weights for edge clauses properly; but, the edge clauses aren't being tagged properly
        # blocker: bug with how we're creating CNFs for exactly N triangles
        raise NotImplementedError

    def pr(self, G, use_cached=False):
        # perform a WMC
        raise NotImplementedError

    def observe_edge(self, G, s, t):
        # adjust the weight to be 1
        raise NotImplementedError

    def observe_no_edge(self, G, s, t):
        # adjust the weight to be 0
        raise NotImplementedError

    def observe_triangle(self, G, a, b, c):
        # call observe edge three times :)
        raise NotImplementedError


def ordered_edges(num_nodes):
    """
    Arbitrarily (but consistently) orders all edges in a graph of size num_nodes.
    Returns:
    1. a list of tuples, where each tuple (a, b) represents an undirected edge
       between nodes a and b (0-indexed).
    2. reverse dictionary, mapping each (a, b) to a unique index
    """
    order = []
    edge_indices = {}
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            edge_indices[(i, j)] = len(order)
            edge_indices[(j, i)] = len(order)
            order.append((i, j))
    return order, edge_indices


def triangle_dnf(num_nodes):
    """
    Returns a DNF where each clause is a possible triangle in
    a graph of size num_nodes.
    Every atom is an index into ordered_edges.
    """
    _, edge_indices = ordered_edges(num_nodes)
    out = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            for k in range(j + 1, num_nodes):
                out.append(
                    [edge_indices[(i, j)], edge_indices[(j, k)], edge_indices[(k, i)]]
                )
    return out


def triangle_cnf(num_nodes):
    """
    Returns a CNF where each clause is a possible triangle in
    a graph of size num_nodes.
    Every atom is an index into ordered_edges. Requires a DNF -> CNF conversion, which is non-trivial.
    """
    return tseitin(triangle_dnf(num_nodes))


def tseitin(dnf):
    """
    Transformation from DNF -> CNF; see https://en.wikipedia.org/wiki/Tseytin_transformation

    Inspired by: https://github.com/Mihiro1ll1/ConvertCNF/blob/master/Tseitin.py
    """

    largest_var = max(max(abs(atom) for atom in term) for term in dnf)
    next_var = largest_var + 1

    ans = []

    for term in dnf:
        ans.append([-1 * term[j] for j in range(len(term))] + [next_var])
        for atom in term:
            ans.append([atom, -1 * next_var])
        next_var += 1

    return ans


def to_dimacs_format(clauses):
    """
    Handles writing to DIMACS format including adding the correct header
    and formatting each clause (1-indexing, 0 terminator).
    """
    largest_var = max(max(abs(atom) for atom in clause) for clause in clauses)

    header = [f"p cnf {largest_var} {len(clauses)}"]
    formatted_clauses = [
        f"{' '.join([str(a + 1) for a in clause])} 0" for clause in clauses
    ]
    return "\n".join(header + formatted_clauses)


def mc(cnf):
    mgr, root = SddManager.from_cnf_string(cnf)
    wmc = root.wmc(log_mode=False)
    w = wmc.propagate()


def bench(lim):
    print("[")
    for num_nodes_step in range(2, lim):
        num_nodes = 2**num_nodes_step
        eprint("num nodes = {}".format(num_nodes))

        times = []

        # temporarily, ignores p/q samples - these don't affect MC
        for _ in range(25):
            start_time = time.time()
            dimacs_format = to_dimacs_format(triangle_cnf(num_nodes))
            # sim: model count for each possible number of triangles
            for _ in range(comb(num_nodes, 3)):
                mc(dimacs_format)
            time_elapsed = time.time() - start_time
            times.append(time_elapsed)

        print(
            f'{{  "n": {num_nodes}, "mean": {str(np.mean(np.array(times)))}, "std": {str(np.std(np.array(times)))}, "times": {times} }},'
        )
    print("]")


def main():
    """
    Main driver (parses args, etc.)
    """
    parser = ArgumentParser(
        prog="cnfgen",
        description="Generates a CNF representing triangle counting for a graph.",
    )
    parser.add_argument("-f", "--file", type=str)
    parser.add_argument("-n", "--nodes", type=int)
    parser.add_argument("-b", "--benchmark", action=BooleanOptionalAction)

    args = parser.parse_args()

    if args.benchmark:
        bench(10)

    else:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(to_dimacs_format(triangle_cnf(args.nodes)))


if __name__ == "__main__":
    main()
