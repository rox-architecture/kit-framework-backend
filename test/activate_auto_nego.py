import requests
import json
import random
import sys


url = "http://localhost:8080/config"

payload = {
    "auto_nego": True
}

response = requests.post(url, json=payload)
print("Status:", response.status_code)
print(response.text)
