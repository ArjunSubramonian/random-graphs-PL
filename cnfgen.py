"""
Module for experimenting with logical formula compilation of clique-counting. Broadly, we generate a DNF representing triangle counting (for an arbitrary graph), perform a Tseitin transform to convert it to a CNF, and then output it in DIMACS form.
"""

from argparse import ArgumentParser


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
    Returns a DNF where each clause is a possible triangle in
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


def to_dimacs_file(fname, clauses):
    """
    Handles writing to a DIMACS-format file, including adding the correct header
    and formatting each clause (1-indexing, 0 terminator).
    """
    largest_var = max(max(abs(atom) for atom in clause) for clause in clauses)

    header = [f"p cnf {largest_var} {len(clauses)}"]
    formatted_clauses = [
        f"{' '.join([str(a + 1) for a in clause])} 0" for clause in clauses
    ]
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(header + formatted_clauses))


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
    # parser.add_argument("-t", "--triangles", type=int, default=1)

    args = parser.parse_args()

    to_dimacs_file(args.file, triangle_cnf(args.nodes))


if __name__ == "__main__":
    main()
