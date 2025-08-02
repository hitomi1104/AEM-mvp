# import requests

# def post_payload(payload, url="https://your-endpoint.com/submit"):
#     try:
#         response = requests.post(url, json=payload, timeout=10)
#         if response.status_code in [200, 201]:
#             return True, response.status_code
#         else:
#             return False, response.status_code
#     except requests.exceptions.RequestException as e:
#         return False, str(e)


import requests
import json
from datetime import datetime

LOG_FILE = "submission.log"
FAILED_FILE = "failed.jsonl"


def post_payload(payload, url):
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code in [200, 201]:
            return {
                "status": "success",
                "code": response.status_code,
                "response": response.json() if response.content else "No content"
            }
        else:
            return {
                "status": "failed",
                "code": response.status_code,
                "error": response.text
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }


def _log_status(status, payload, detail):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {status}: {payload.get('reportId', 'N/A')} → {detail}\n")


def _save_failed_payload(payload):
    with open(FAILED_FILE, "a") as f:
        f.write(json.dumps(payload) + "\n")

def submit_with_logging(payload, url):
    result = post_payload(payload, url)

    if result["status"] == "success":
        _log_status("SUCCESS", payload, f"Code {result['code']}")
    else:
        _log_status("FAILURE", payload, result.get("error", "Unknown error"))
        _save_failed_payload(payload)

    return result