from typing import Any

import networkx as nx


class SequenceGenerator:
    """Scheduler for workflows."""

    def __init__(self, graph_json: dict[str, Any]) -> None:
        """Initialize the instance."""
        self.graph_json = graph_json
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        """Build a DAG."""
        graph = nx.DiGraph()

        for node in self.graph_json.get("nodes", []):
            graph.add_node(node["id"], **node)

        for edge in self.graph_json.get("edges", []):
            graph.add_edge(edge["source"], edge["target"], **edge)

        return graph

    def check_dag(self) -> bool:
        """Verify the DAG."""
        return nx.is_directed_acyclic_graph(self.graph)

    # topological generation sort
    def generate_plan(self) -> list[list[str]]:
        """Generate a plan."""
        # return 2d list, where each element is 1d to enable parallelisation in the future
        # TODO: efficient DAG execution order calculation algorithm is needed: minimisation of memory footage and maximisation of the parallelisation
        return [[level] for level in nx.topological_sort(self.graph)]
