from pgmpy.models import BayesianNetwork as BN
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import itertools
import numpy as np

class BayesianNetwork:
    def pr(self, G, use_cached=False):
        if not use_cached:
            cpds = {}
            for u1, u2 in itertools.combinations(list(range(G.num_nodes)), 2):
                edge_node = str(u1) + "_" + str(u2)

                if u2 in G.out_adj_list[u1]:
                    prob = G.out_adj_list[u1][u2]
                elif u1 in G.out_adj_list[u2]:
                    prob = G.out_adj_list[u2][u1]
                else:
                    prob = 0.0

                cpds[edge_node] = TabularCPD(
                    variable=edge_node,
                    variable_card=2,
                    values=[[1 - prob], [prob]],
                )

            edges = []
            tri_nodes = []
            for subset in itertools.combinations(list(range(G.num_nodes)), 3):
                n1, n2, n3 = subset
                tri_node = str(n1) + "_" + str(n2) + "_" + str(n3)
                tri_nodes.append(tri_node)

                evidence = []
                for u1, u2 in itertools.combinations(subset, 2):
                    edge_node = str(u1) + "_" + str(u2)
                    evidence.append(edge_node)

                cpds[tri_node] = TabularCPD(
                    variable=tri_node,
                    variable_card=2,
                    values=[
                        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                    ],
                    evidence=evidence,
                    evidence_card=[2, 2, 2],
                )

                for edge_node in evidence:
                    edges.append((edge_node, tri_node))

            num_tri_nodes = len(tri_nodes)
            sum_cpd = np.array([list(i) for i in itertools.product([0, 1], repeat=num_tri_nodes)])
            sum_cpd = sum_cpd.sum(axis=1)
            sum_cpd = np.eye(num_tri_nodes + 1)[sum_cpd].T

            cpds['sum'] = TabularCPD(
                    variable='sum',
                    variable_card=num_tri_nodes + 1,
                    values=sum_cpd.tolist(),
                    evidence=tri_nodes,
                    evidence_card=[2 for _ in range(num_tri_nodes)],
                )
            for tri_node in tri_nodes:
                edges.append((tri_node, 'sum'))

            graph_model = BN(edges)
            graph_model.add_cpds(*list(cpds.values()))
            self.graph_infer = VariableElimination(graph_model)
        
        evidence = {
            str(s) + "_" + str(t) : pos for (s, t), pos in G.observations
        }
        q = self.graph_infer.query(variables=['sum'], evidence=evidence)
        dist = dict(zip(list(range(len(q.values))), q.values))
        return dist