import requests
import json

URL = "https://vision-x-api.base-x-ecosystem.org/connectors/jin-conn/cp/management/v3/edrs/request"

payload = {
    "@context": {},
    "@type": "QuerySpec",
    "filterExpression": [
        {
            "operandLeft": "assetId",
            "operator": "=",
            "operandRight": "Fashion MNIST trainset",
        }
    ],
}

headers = {
    "Authorization": "Bearer sk-72eebed08d3d0a78b24f1341c23230e165cd9d3e27ffb9cc768a57bce86be32c",
}

response = requests.post(
    URL,
    headers=headers,
    json=payload,
    timeout=30,
)
