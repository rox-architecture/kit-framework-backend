import requests
import json
import random
import sys

url = "http://localhost:8080/workflows"
filename = sys.argv[1]

with open(filename, "r", encoding="utf-8") as f:
    graph_json = json.load(f)

n = random.randint(1, 1000)
payload = {"workflow_name": f"my-workflow{n}", "graph_json": graph_json}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print(response.text)
