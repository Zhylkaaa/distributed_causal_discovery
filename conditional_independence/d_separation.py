from typing import Set

import networkx as nx

from conditional_independence.base_ci_test import BaseCITest


class OracleCI(BaseCITest):
    def __init__(self, true_dag: nx.DiGraph):
        self.true_dag = true_dag

    def __call__(self, x: int, y: int, cond_set: Set[int]):
        return nx.d_separated(self.true_dag, {x}, {y}, cond_set)
