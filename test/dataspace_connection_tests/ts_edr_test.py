import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path("../..") / ".env")

base_url = os.getenv("BASE_URL_TS_CONNECTOR")
api_key = os.getenv("API_KEY_TS_CONNECTOR")
endpoint = "data/v2/edrs/request"
full_url = f'{base_url}/{endpoint}' 

CONTEXT = {
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "tx": "https://w3id.org/tractusx/v0.0.1/ns/",   
    "tx-auth": "https://w3id.org/tractusx/auth/",
    "cx-policy": "https://w3id.org/catenax/policy/",
    "dct": "http://purl.org/dc/terms/type/",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "dspace": "https://w3id.org/dspace/v0.8/",
    "cx-common:": "https://w3id.org/catenax/toxonomy#",
    "aas-sematics": "https://admin-shell.io/aas/3/0/HasSemantics"
}

"""For DLR dataspace"""
# headers = {
#     "Authorization": f"Bearer {api_key}"
# }

"""For T-System dataspace"""
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": f"{api_key}"
}

"""Payload"""
payload = {
    "@context": CONTEXT,
    "type": "QuerySpec",
    "offset": 0,
    "limit": 1000,
}

response = requests.post(
    full_url,
    headers=headers,
    json=payload,
    timeout=30,
)

print(full_url)
print(response.status_code)
print(response.headers)
try:
    print(json.dumps(response.json(), indent=2))
except ValueError:
    print(response.text)