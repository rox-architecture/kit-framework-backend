import requests
import json

url = "http://localhost:8080/workflows"

with open("ex1.json", "r", encoding="utf-8") as f:
    graph_json = json.load(f)

payload = {
    "workflow_name": "my-workflow2",
    "graph_json": graph_json
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print(response.text)