from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
import ray

from conditional_independence.base_ci_test import BaseCITest
from conditional_independence.d_separation import OracleCI
from graph.causal_graph import CausalGraph

ray.init()


@ray.remote
def find_edges_to_remove(x, y, candidates, depth, ci):
    remove_edges = []

    for cond_set in combinations(candidates, depth):
        if ci(x, y, cond_set):
            remove_edges.append((x, y))
    return remove_edges


class PCAlgorithm:
    def __init__(self, num_variables: int, cond_independence_test: BaseCITest):
        self.num_variables = num_variables
        self.ci_test = ray.put(cond_independence_test)
        self.causal_graph = CausalGraph(num_variables, is_directed=False)

    def learn_skeleton(self):
        depth = 0

        while depth < self.causal_graph.max_degree():
            print(f'Depth {depth}')
            edges_to_remove = []
            for x in range(self.num_variables):
                x_neighbors = set(self.causal_graph.neighbors(x))
                if len(x_neighbors) < depth - 1:
                    continue
                for y in x_neighbors:
                    # banned_edge = self.check_knowledge_base(x, y)
                    edges_to_remove.append(
                        find_edges_to_remove.remote(x, y, x_neighbors - {y}, depth, self.ci_test)
                    )
            while len(edges_to_remove):
                (done_id,), edges_to_remove = ray.wait(edges_to_remove)
                remove_edges = ray.get(done_id)
                print(remove_edges)
                for x, y in remove_edges:
                    if self.causal_graph.has_edge(x, y):
                        self.causal_graph.remove_edge(x, y)
            depth += 1

    def orient_edges(self):
        pass  # TODO

    def run_discovery(self):
        self.learn_skeleton()
        # self.orient_edges()


if __name__ == '__main__':
    true_graph = nx.DiGraph()
    [true_graph.add_node(i) for i in range(4)]
    true_graph.add_edge(0, 1)
    true_graph.add_edge(0, 2)
    true_graph.add_edge(1, 3)
    true_graph.add_edge(2, 3)
    ci_test = OracleCI(true_graph)

    pc_alg = PCAlgorithm(4, cond_independence_test=ci_test)
    pc_alg.run_discovery()

    nx.draw(pc_alg.causal_graph.G)
    plt.show()
