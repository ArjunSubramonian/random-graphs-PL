"""
Generate plots used for presentation/final report.
"""

import json
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "text.usetex": True,
    }
)


def main():
    with open("benches/mc.json", encoding="utf-8") as f:
        mc = json.load(f)

    with open("benches/mcmc.json", encoding="utf-8") as f:
        mcmc = json.load(f)

    with open("benches/database.json", encoding="utf-8") as f:
        database = json.load(f)

    with open("benches/bn.json", encoding="utf-8") as f:
        bn = json.load(f)

    with open("benches/sdd.json", encoding="utf-8") as f:
        sdd = json.load(f)

    def plot_bench(data, label):
        plt.errorbar(
            [bench["n"] for bench in data],
            [bench["mean"] for bench in data],
            [bench["std"] for bench in data],
            ecolor="black",
            label=label,
        )

    plot_bench(mc, "MC")
    plot_bench(mcmc, "MCMC")
    plot_bench(database, "naive PDB")
    plot_bench(bn, "Bayesian Network")
    plot_bench(sdd, "WMC (SDD-based)")

    plt.xlabel("n = number of nodes in graph")
    plt.ylabel("wall clock time (s)")
    plt.title(
        "scaling different graph implementations over node count\nover 25 runs in $P \\times Q$, $P, Q \\in \\{0.2, 0.4, 0.6, 0.8, 1\\}$"
    )
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
