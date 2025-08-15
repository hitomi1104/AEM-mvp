# import requests
# import json
# from datetime import datetime

# LOG_FILE = "submission.log"
# FAILED_FILE = "failed.jsonl"


# def post_payload(payload, url):
#     try:
#         if url.endswith("/test-post"):
#             # Send as multipart file upload
#             files = {
#                 'file': ('retry.json', json.dumps(payload), 'application/json')
#             }
#             response = requests.post(url, files=files, timeout=30)
#         else:
#             # Default: send as raw JSON
#             response = requests.post(url, json=payload, timeout=30)

#         if response.status_code in [200, 201]:
#             return {
#                 "status": "success",
#                 "code": response.status_code,
#                 "response": response.json() if response.content else "No content"
#             }
#         else:
#             return {
#                 "status": "failed",
#                 "code": response.status_code,
#                 "error": response.text
#             }

#     except requests.exceptions.RequestException as e:
#         return {
#             "status": "error",
#             "error": str(e)
#         }


# def _log_status(status, payload, detail):
#     timestamp = datetime.utcnow().isoformat()
#     log_line = f"[{timestamp}] {status}: {payload.get('reportId', 'N/A')} → {detail}"
#     print("LOGGING TO submission.log:", log_line)  # Debug print
#     with open(LOG_FILE, "a") as log:
#         log.write(log_line + "\n")
# def _save_failed_payload(payload: dict):
#     from datetime import datetime
#     log_entry = {
#         "timestamp": datetime.utcnow().isoformat(),
#         "payload": payload
#     }
#     print("SAVING TO failed.jsonl:", log_entry)  # Debug print
#     with open(FAILED_FILE, "a") as f:
#         f.write(json.dumps(log_entry) + "\n")

# def submit_with_logging(payload, url):
#     result = post_payload(payload, url)

#     if result["status"] == "success":
#         _log_status("SUCCESS", payload, f"Code {result['code']}")
#     else:
#         _log_status(
#             "FAILURE", 
#             payload, 
#             f"{result.get('error', 'Unknown error')} → Code {result.get('code', 'N/A')}"
#         )
#         _save_failed_payload(payload)

#     return result


# def retry_failed_payloads(url):
#     import os

#     if not os.path.exists(FAILED_FILE):
#         print("No failed submissions to retry.")
#         return

#     new_failures = []
#     with open(FAILED_FILE, "r") as f:
#         for line in f:
#             try:
#                 payload = json.loads(line.strip())
#                 result = post_payload(payload, url)

#                 if result["status"] == "success":
#                     _log_status("RETRY SUCCESS", payload, f"Code {result['code']}")
#                 else:
#                     _log_status(
#                         "RETRY FAILURE", 
#                         payload, 
#                         f"{result.get('error', 'Unknown error')} → Code {result.get('code', 'N/A')}"
#                     )
#                     new_failures.append(payload)

#             except json.JSONDecodeError as e:
#                 _log_status("RETRY ERROR", {"reportId": "N/A"}, f"Invalid JSON line → {str(e)}")

#     # Overwrite failed.jsonl with only the new failures
#     with open(FAILED_FILE, "w") as f:
#         for item in new_failures:
#             f.write(json.dumps(item) + "\n")

#     print(f"Retry complete. {len(new_failures)} still failed.")




import requests
import json
from datetime import datetime

LOG_FILE = "submission.log"
FAILED_FILE = "failed.jsonl"

def post_payload(payload, url):
    try:
        # For /test-post we send as a file to exercise both code paths
        if url.endswith("/test-post"):
            files = {'file': ('payload.json', json.dumps(payload), 'application/json')}
            response = requests.post(url, files=files, timeout=30)
        else:
            response = requests.post(url, json=payload, timeout=30)

        if response.status_code in (200, 201):
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
        return {"status": "error", "error": str(e)}

def _log_status(status, payload, detail):
    ts = datetime.utcnow().isoformat()
    rid = payload.get("reportId", "N/A") if isinstance(payload, dict) else "N/A"
    with open(LOG_FILE, "a") as log:
        log.write(f"[{ts}] {status}: {rid} → {detail}\n")

def _save_failed_payload(payload: dict):
    # Always store just the payload, plus a retry_count
    rec = dict(payload)
    rec["retry_count"] = int(rec.get("retry_count", 0))
    with open("failed.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")

def retry_failed_payloads(url, max_passes=1):
    """
    Simple retry loop over failed.jsonl.
    max_passes=1 means: make one pass through current file.
    (You can call this on a schedule to emulate unlimited retries.)
    """
    import os

    if not os.path.exists(FAILED_FILE):
        print("No failed submissions to retry.")
        return

    remaining = []
    with open(FAILED_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            # Each line is {"timestamp": "...", "payload": {...}}
            try:
                wrapped = json.loads(line.strip())
                payload = wrapped.get("payload", {})
            except json.JSONDecodeError as e:
                _log_status("RETRY ERROR", {"reportId": "N/A"}, f"Invalid JSON line → {str(e)}")
                continue

            result = post_payload(payload, url)
            if result["status"] == "success":
                _log_status("RETRY SUCCESS", payload, f"Code {result['code']}")
            else:
                code_txt = f"Code {result.get('code', 'N/A')}"
                _log_status("RETRY FAILURE", payload, f"{result.get('error','Unknown error')} → {code_txt}")
                remaining.append(wrapped)  # keep the same structure

    # overwrite with only the ones still failing
    with open(FAILED_FILE, "w") as f:
        for item in remaining:
            f.write(json.dumps(item) + "\n")

    print(f"Retry complete. {len(remaining)} still failed.")


"""
Calls post_payload, logs SUCCESS/FAILURE, and appends to failed.jsonl on failure.
Returns the result dict from post_payload.
"""
def submit_with_logging(payload, url):
    result = post_payload(payload, url)

    if result.get("status") == "success" and result.get("code") in (200, 201):
        _log_status("SUCCESS", payload, f"Code {result['code']}")
    else:
        # include HTTP code in the log detail if we have it
        detail = f"{result.get('error', 'Unknown error')} → Code {result.get('code', 'N/A')}"
        _log_status("FAILURE", payload, detail)
        _save_failed_payload(payload)

    return result