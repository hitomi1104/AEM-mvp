import requests
import json
from datetime import datetime

LOG_FILE = "submission.log"
FAILED_FILE = "failed.jsonl"


def post_payload(payload, url):
    try:
        if url.endswith("/test-post"):
            # Send as multipart file upload
            files = {
                'file': ('retry.json', json.dumps(payload), 'application/json')
            }
            response = requests.post(url, files=files, timeout=30)
        else:
            # Default: send as raw JSON
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
    if "retry_count" not in payload:
        payload["retry_count"] = 1
    else:
        payload["retry_count"] += 1

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


def retry_failed_payloads(url):
    import os

    if not os.path.exists(FAILED_FILE):
        print("No failed submissions to retry.")
        return

    new_failures = []
    with open(FAILED_FILE, "r") as f:
        for line in f:
            try:
                payload = json.loads(line.strip())
                result = post_payload(payload, url)

                if result["status"] == "success":
                    _log_status("RETRY SUCCESS", payload, f"Code {result['code']}")
                else:
                    _log_status("RETRY FAILURE", payload, result.get("error", "Unknown error"))
                    new_failures.append(payload)

            except json.JSONDecodeError as e:
                _log_status("RETRY ERROR", {"reportId": "N/A"}, f"Invalid JSON line → {str(e)}")

    # Overwrite failed.jsonl with only the new failures
    with open(FAILED_FILE, "w") as f:
        for item in new_failures:
            f.write(json.dumps(item) + "\n")

    print(f"Retry complete. {len(new_failures)} still failed.")