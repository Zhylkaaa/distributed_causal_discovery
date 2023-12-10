from typing import Union
import networkx as nx


class CausalGraph:
    def __init__(self, num_nodes, is_directed=False):
        self.is_directed = is_directed
        g_t = nx.DiGraph if is_directed else nx.Graph
        self.G: Union[nx.DiGraph, nx.Graph] = nx.complete_graph(num_nodes, create_using=g_t())

    def neighbors(self, x):
        return self.G.neighbors(x)

    def max_degree(self):
        return max(d for n, d in self.G.degree())

    def add_edge(self, x, y):
        self.G.add_edge(x, y)

    def remove_edge(self, x, y):
        self.G.remove_edge(x, y)

    def has_edge(self, x, y):
        return self.G.has_edge(x, y)
