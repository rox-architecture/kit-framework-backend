import json
from cee.graph_parser import GraphParser

with open("../ex1.json", "r", encoding="utf-8") as f:
    graph_json = json.load(f)

p = GraphParser(graph_json)

node_fetch = p.get_node_by_label("SoftwareA")
print(node_fetch)
