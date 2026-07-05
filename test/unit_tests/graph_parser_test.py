import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.graph_parser import GraphParser



with open("../ex1.json", "r", encoding="utf-8") as f:
    graph_json = json.load(f)

p = GraphParser(graph_json)

node_fetch = p.get_node_by_label('SoftwareA')
print(node_fetch)