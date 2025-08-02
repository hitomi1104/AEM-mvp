# test_request.py
import requests

payload = {
    "test": "value"
}

response = requests.post(
    "http://127.0.0.1:8000/generate-json-lsmv",
    json=payload,
    timeout=10
)

print("Status:", response.status_code)
print("Response:", response.json())

