

import requests
import json
from datetime import datetime

LOG_FILE = "submission.log"
FAILED_FILE = "failed.jsonl"

def post_payload(payload, url):
    try:
        if url.endswith("/test-post"):
            files = {'file': ('payload.json', json.dumps(payload), 'application/json')}
            resp = requests.post(url, files=files, timeout=30)
        else:
            resp = requests.post(url, json=payload, timeout=30)

        if resp.status_code in (200, 201):
            return {"status": "success", "code": resp.status_code,
                    "response": resp.json() if resp.content else "No content"}
        else:
            # Server returned a non-2xx — we have an HTTP code
            return {"status": "failed", "code": resp.status_code,
                    "error": resp.text or f"HTTP {resp.status_code}"}

    except requests.exceptions.RequestException as e:
        # Network/client errors — no HTTP code
        return {"status": "error", "code": None, "error": str(e)}


def _log_status(status: str, payload: dict, detail: str, code: int | None = None, logfile: str = LOG_FILE):
    rid = (payload or {}).get("reportId", "N/A")
    ts = datetime.utcnow().isoformat()
    line = f"[{ts}] {status}: {rid} → {detail}"
    if code is not None:
        line += f" → Code {code}"
    with open(logfile, "a") as f:
        f.write(line + "\n")

def _save_failed_payload(payload: dict, error_msg: str = "", failed_path: str = FAILED_FILE):
    rec = {
        "payload": payload,
        "retry_count": 0,
        "first_seen": datetime.utcnow().isoformat(),
        "last_error": error_msg,
    }
    with open(failed_path, "a") as f:
        f.write(json.dumps(rec) + "\n")


def submit_with_logging(payload, url):
    result = post_payload(payload, url)

    if result["status"] == "success":
        _log_status("SUCCESS", payload, "OK", code=result.get("code", 200))
    elif result["status"] == "failed":
        _log_status("FAILURE", payload, result.get("error", "Unknown error"), code=result.get("code"))
        _save_failed_payload(payload, last_error=result.get("error"))
    else:  # "error" (network/timeouts)
        _log_status("FAILURE", payload, result.get("error", "Unknown error"), code=None)
        _save_failed_payload(payload, last_error=result.get("error"))

    return result


def retry_failed_payloads(url, max_retries=3):
    """Legacy helper kept for compatibility (runner uses its own loop)."""
    import os
    if not os.path.exists(FAILED_FILE):
        print("No failed submissions to retry.")
        return

    kept = []
    with open(FAILED_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                # Accept both schemas:
                if "payload" in obj:
                    payload = obj["payload"]
                    retry_count = int(obj.get("retry_count", 0))
                else:
                    payload = obj
                    retry_count = int(payload.get("retry_count", 0))

                if retry_count >= max_retries:
                    kept.append(obj)  # keep for next time
                    continue

                res = post_payload(payload, url)
                if res["status"] == "success":
                    _log_status("RETRY SUCCESS", payload, "OK", code=res.get("code", 200))
                    # drop it
                elif res["status"] == "failed":
                    _log_status("RETRY FAILURE", payload, res.get("error", "Unknown error"), code=res.get("code"))
                    # increment and keep
                    if "payload" in obj:
                        obj["retry_count"] = retry_count + 1
                        obj["last_error"] = res.get("error", "")
                        kept.append(obj)
                    else:
                        payload["retry_count"] = retry_count + 1
                        kept.append(payload)
                else:
                    _log_status("RETRY FAILURE", payload, res.get("error", "Unknown error"), code=None)
                    if "payload" in obj:
                        obj["retry_count"] = retry_count + 1
                        obj["last_error"] = res.get("error", "")
                        kept.append(obj)
                    else:
                        payload["retry_count"] = retry_count + 1
                        kept.append(payload)
            except Exception as e:
                _log_status("RETRY ERROR", {"reportId": "N/A"}, f"Invalid JSONL line → {str(e)}", code=None)

    with open(FAILED_FILE, "w") as f:
        for item in kept:
            f.write(json.dumps(item) + "\n")

    print(f"Retry complete. {len(kept)} still failed.")