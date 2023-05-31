"""
Generate plots used for technical report.
"""

from math import comb
import matplotlib.pyplot as plt

from cnfgen import triangle_cnf

plt.rcParams.update(
    {
        "text.usetex": True,
    }
)


def plot_versus_n(data, ns, title, ylabel):
    plt.plot(ns, data)
    plt.xlabel("n = number of nodes in graph")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def main():
    n = 100
    vals = range(3, n + 1)

    num_triangles = [comb(i, 3) for i in vals]

    cnfs = [triangle_cnf(i) for i in vals]
    num_clauses = [len(cnf) for cnf in cnfs]
    num_vars = [
        max(max(abs(atom) for atom in clause) for clause in cnf) for cnf in cnfs
    ]

    plot_versus_n(
        num_triangles,
        vals,
        f"Potential triangles versus size of graph ($n \leq {n}$)",
        "Total number of possible triangles = $C(n, 3)$",
    )

    plot_versus_n(
        num_vars,
        vals,
        f"Variables in CNF versus size of graph ($n \leq {n}$)",
        "Number of Variables in CNF (including Tseitin additions)",
    )

    plot_versus_n(
        num_clauses,
        vals,
        f"Clauses in CNF versus size of graph ($n \leq {n}$)",
        "Clauses in CNF",
    )


if __name__ == "__main__":
    main()
