import networkx as nx
from typing import Any

class GraphParser:

    def __init__(self, graph_json):
        self.graph_json = graph_json
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()

        id_to_label = {}

        for node in self.graph_json.get("nodes", []):
            label = node["data"]["label"]
            id_to_label[node["id"]] = label
            graph.add_node(label, **node)

        for edge in self.graph_json.get("edges", []):
            source = id_to_label[edge["source"]]
            target = id_to_label[edge["target"]]
            graph.add_edge(source, target, **edge)

        return graph

    def check_DAG(self) -> bool:
        return nx.is_directed_acyclic_graph(self.graph)

    # topological generation sort
    def generate_plan(self) -> list[list[str]]:
        return [list(level) for level in nx.topological_generations(self.graph)]
    