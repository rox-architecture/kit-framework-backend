import requests

EDC_CONTEXT = {
    "tx": "https://w3id.org/tractusx/v0.0.1/ns/",
    "tx-auth": "https://w3id.org/tractusx/auth/",
    "cx-policy": "https://w3id.org/catenax/2025/9/policy/",
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "dspace": "https://w3id.org/dspace/v0.8/",
}

base_url = "https://vision-x-api.base-x-ecosystem.org/connectors/lea-conn"
api_key = ""
provider_bpn = "BPNLE56YR9OQVTA3"
provider_url = "https://vision-x-api.base-x-ecosystem.org/connectors/lea-conn/cp/protocol"
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {api_key}"})

endpoint = "cp/management/v3/catalog/request"
url = f"{base_url}/{endpoint}"
payload = {
    "@context": EDC_CONTEXT,
    "counterPartyAddress": str(provider_url),
    "counterPartyId": provider_bpn,
    "protocol": "dataspace-protocol-http",
    "querySpec": {
        "offset": 0,
        "limit": 10000,
    },
}

response = session.post(url, json=payload)
response.raise_for_status()
print(response.json())
