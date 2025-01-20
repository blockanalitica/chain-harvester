import requests


def call_graphql(url, query, variables=None):
    payload = {"query": query, "variables": variables}
    headers = {"accept": "application/json", "content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    return response.json()
