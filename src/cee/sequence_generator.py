from typing import Any

import networkx as nx


class SequenceGenerator:
    """Scheduler for workflows."""

    def __init__(self, graph_json: dict[str, Any]) -> None:
        """Initialize the instance."""
        self.graph_json = graph_json
        self.graph: nx.DiGraph[str] = self._build_graph()

    def _build_graph(self) -> nx.DiGraph[str]:
        """Build a DAG."""
        graph: nx.DiGraph[str] = nx.DiGraph()

        for node in self.graph_json.get("nodes", []):
            graph.add_node(node["id"], **node)

        for edge in self.graph_json.get("edges", []):
            graph.add_edge(edge["source"], edge["target"], **edge)

        return graph

    def check_dag(self) -> bool:
        """Verify the DAG."""
        return nx.is_directed_acyclic_graph(self.graph)

    def generate_plan(self) -> dict[str, dict[str, list[str]] | list[str]]:
        """Generate dependency metadata for dynamic, readiness-based scheduling."""
        return {
            "predecessors": {
                str(node): [str(value) for value in self.graph.predecessors(node)]
                for node in self.graph.nodes
            },
            "successors": {
                str(node): [str(value) for value in self.graph.successors(node)]
                for node in self.graph.nodes
            },
            "roots": [
                str(node) for node, degree in self.graph.in_degree() if degree == 0
            ],
        }
