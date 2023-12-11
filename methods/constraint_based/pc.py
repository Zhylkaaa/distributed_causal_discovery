import os
import sys
from itertools import combinations
from functools import partial
import pickle

import matplotlib.pyplot as plt
import networkx as nx
import ray
from loky import get_reusable_executor

from conditional_independence.base_ci_test import BaseCITest
from conditional_independence.d_separation import OracleCI
from graph.causal_graph import CausalGraph


assert len(sys.argv) < 4, "too many arguments"
true_graph_path = sys.argv[1]
if len(sys.argv) == 3:
    actor_cpus = int(sys.argv[2])
else:
    actor_cpus = 1

ray.init(address=os.environ.get("ip_head"))


@ray.remote(num_cpus=actor_cpus)
def find_edges_to_remove(x, y, candidates, depth, ci, num_threads=1):
    if num_threads <= 1:
        for cond_set in combinations(candidates, depth):
            if ci(x, y, cond_set):
                return x, y
    else:
        with get_reusable_executor(max_workers=num_threads) as executor:
            ci_test = partial(ci, x, y)
            ind_tests = executor.map(ci_test, combinations(candidates, depth))
            if any(ind_tests):
                return x, y
    return None


class PCAlgorithm:
    def __init__(self, num_variables: int, cond_independence_test: BaseCITest, num_threads=1):
        self.num_variables = num_variables
        self.ci_test = ray.put(cond_independence_test)
        self.causal_graph = CausalGraph(num_variables, is_directed=False)
        self.num_threads = num_threads

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
                        find_edges_to_remove.remote(x, y, x_neighbors - {y},
                                                    depth,
                                                    self.ci_test,
                                                    self.num_threads)
                    )
            while len(edges_to_remove):
                (done_id,), edges_to_remove = ray.wait(edges_to_remove)
                remove_edge = ray.get(done_id)
                print(remove_edge)
                if remove_edge:
                    x, y = remove_edge
                    if self.causal_graph.has_edge(x, y):
                        self.causal_graph.remove_edge(x, y)
            depth += 1

    def orient_edges(self):
        pass  # TODO

    def run_discovery(self):
        self.learn_skeleton()
        # self.orient_edges()


if __name__ == '__main__':
    with open(true_graph_path, 'rb') as f:
        true_graph: nx.DiGraph = pickle.load(f)
    ci_test = OracleCI(true_graph)

    pc_alg = PCAlgorithm(true_graph.number_of_nodes(), cond_independence_test=ci_test, num_threads=actor_cpus)
    pc_alg.run_discovery()

    nx.draw(pc_alg.causal_graph.G)
    plt.show()
