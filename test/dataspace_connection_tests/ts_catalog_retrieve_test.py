import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path("../..") / ".env")

base_url = os.getenv("BASE_URL_TS_CONNECTOR")
api_key = os.getenv("API_KEY_TS_CONNECTOR")
endpoint = "data/v2/catalog/request"
full_url = f'{base_url}/{endpoint}' 


"""For DLR dataspace"""
# headers = {
#     "Authorization": f"Bearer {api_key}"
# }


"""For T-System dataspace"""
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": f"{api_key}"
}

provider_bpn = "BPNL000000000065"
provider_endpoint = "https://t-syst-9e114f1c-de.rox-test.lila.dih.telekom.com"
asset_id = "CI_test_03"

"""Payload"""
payload = {
            "@context": {
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
            },
            "@type": "CatalogRequest",
            "protocol": "dataspace-protocol-http",
            "counterPartyId": provider_bpn,
            "counterPartyAddress": provider_endpoint + "/api/v1/dsp",
            "querySpec": {
                "offset": 0,
                "limit": 20000,
                "sortField": "target",
                "sortOrder": "DESC",
                "filterExpression": [
                ]
            }
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
    print(response.json())

print("-------------------------------------------")

for dataset in response.json()['dcat:dataset']:
    if dataset["@id"] != asset_id:
        continue
    print(dataset)
