import os
import sys
from itertools import combinations
from concurrent.futures import as_completed
import pickle

import matplotlib.pyplot as plt
import networkx as nx
import ray
from loky import get_reusable_executor
from loky.backend import get_context

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
    if num_threads <= 1 or depth == 0:
        for cond_set in combinations(candidates, depth):
            if ci(x, y, cond_set):
                return x, y
    else:
        with get_reusable_executor(max_workers=num_threads, context=get_context('loky')) as executor:
            ind_tests = [executor.submit(ci, x, y, cond_set) for cond_set in combinations(candidates, depth)]
            for r in as_completed(ind_tests):
                if r.result():
                    executor.shutdown()
                    return x, y
    return None


class PCAlgorithm:
    def __init__(self,
                 num_variables: int,
                 cond_independence_test: BaseCITest,
                 num_threads=1,
                 collection_batch=512,
                 concurrent_tasks=1024):
        self.num_variables = num_variables
        self.ci_test = ray.put(cond_independence_test)
        self.causal_graph = CausalGraph(num_variables, is_directed=False)
        self.num_threads = num_threads
        self.edges_to_prune = []
        self.collection_batch = collection_batch
        self.concurrent_tasks = concurrent_tasks

    def learn_skeleton(self):
        depth = 0

        while depth < self.causal_graph.max_degree():
            print(f'Depth {depth}')
            edges_to_remove = []
            pairs_launched = set()
            for x in range(self.num_variables):
                x_neighbors = set(self.causal_graph.neighbors(x))
                if len(x_neighbors) < depth - 1:
                    continue
                for y in x_neighbors:
                    pair = tuple(sorted((x, y)))
                    if pair in pairs_launched:
                        continue
                    pairs_launched.add(pair)
                    # banned_edge = self.check_knowledge_base(x, y)
                    edges_to_remove.append(
                        find_edges_to_remove.remote(x, y, x_neighbors - {y},
                                                    depth,
                                                    self.ci_test,
                                                    self.num_threads)
                    )
                while len(edges_to_remove) >= self.concurrent_tasks:
                    edges_to_remove = self._wait_and_process_results(edges_to_remove, batch_size=self.collection_batch)

            _ = self._wait_and_process_results(edges_to_remove, batch_size=len(edges_to_remove))
            for x, y in self.edges_to_prune:
                if self.causal_graph.has_edge(x, y):
                    self.causal_graph.remove_edge(x, y)
            self.edges_to_prune = []
            depth += 1

    def _wait_and_process_results(self, awaitables, batch_size=512):
        batch_size = min(batch_size, len(awaitables))
        done_ids, awaitables = ray.wait(awaitables, num_returns=batch_size)
        results = ray.get(done_ids)
        for remove_edge in results:
            if remove_edge:
                self.edges_to_prune.append(remove_edge)
        return awaitables

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
