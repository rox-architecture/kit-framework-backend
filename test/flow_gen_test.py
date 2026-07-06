import requests
import json
import random

url = "http://localhost:8080/workflows"

with open("ex2.json", "r", encoding="utf-8") as f:
    graph_json = json.load(f)

n = random.randint(1, 1000)
payload = {"workflow_name": f"my-workflow{n}", "graph_json": graph_json}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print(response.text)
