import requests
import json
import random
import sys

url = "http://localhost:8080/execution/request"
workflow_id = sys.argv[1]

payload = {
    "workflow_id": workflow_id
}

response = requests.post(url, json=payload)
print("Status:", response.status_code)
print(response.text)
