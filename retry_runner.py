# import argparse
# import json
# from datetime import datetime
# from app.poster import post_payload, _log_status, FAILED_FILE

# def load_failed_lines(path):
#     items = []
#     try:
#         with open(path, "r") as f:
#             for line in f:
#                 line = line.strip()
#                 if not line:
#                     continue
#                 try:
#                     obj = json.loads(line)
#                     items.append(obj)
#                 except json.JSONDecodeError:
#                     # Skip malformed line but keep going
#                     _log_status("RETRY ERROR", {"reportId": "N/A"}, "Invalid JSON in failed.jsonl", code=None)
#     except FileNotFoundError:
#         pass
#     return items

# def save_failed_lines(path, items):
#     with open(path, "w") as f:
#         for obj in items:
#             f.write(json.dumps(obj) + "\n")

# def get_wrapped(obj):
#     """Return (wrapper, payload_dict_ref). If wrapper has 'payload', give its ref.
#        Else treat the wrapper itself as payload for backward compatibility."""
#     if isinstance(obj, dict) and "payload" in obj and isinstance(obj["payload"], dict):
#         return obj, obj["payload"]
#     return obj, obj  # compat

# def ensure_meta(wrapper):
#     """Ensure wrapper carries retry_count, first_seen, last_error (without touching payload)."""
#     if "retry_count" not in wrapper:
#         wrapper["retry_count"] = 0
#     if "first_seen" not in wrapper:
#         wrapper["first_seen"] = datetime.utcnow().isoformat()
#     if "last_error" not in wrapper:
#         wrapper["last_error"] = ""
#     return wrapper

# if __name__ == "__main__":
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--url", required=True, help="endpoint to post to (e.g., http://localhost:8000/test-post)")
#     ap.add_argument("--max", type=int, default=3, help="max retries per payload this run")
#     ap.add_argument("--strip-trigger-fail", action="store_true",
#                     help="remove triggerFail from payloads before retry (useful for demos)")
#     args = ap.parse_args()

#     items = load_failed_lines(FAILED_FILE)
#     kept = []

#     for obj in items:
#         wrapper, payload = get_wrapped(obj)
#         ensure_meta(wrapper)

#         # Respect max per-run retries
#         if wrapper["retry_count"] >= args.max:
#             kept.append(wrapper)
#             continue

#         # Optional cleanup of simulation flag for this retry run
#         if args.strip_trigger_fail:
#             if "triggerFail" in payload:
#                 payload.pop("triggerFail", None)

#         # Perform retry
#         res = post_payload(payload, args.url)

#         if res["status"] == "success":
#             # Log and DROP from queue
#             _log_status("RETRY SUCCESS", payload, "OK", code=res.get("code", 200))
#             continue

#         # Failed or error → update metadata and keep
#         wrapper["retry_count"] += 1
#         wrapper["last_error"] = res.get("error", "Unknown error")
#         status = "RETRY FAILURE"
#         code = res.get("code", None)
#         _log_status(status, payload, wrapper["last_error"], code=code)

#         kept.append(wrapper)

#     save_failed_lines(FAILED_FILE, kept)
#     print(f"\nRetry complete. {len(kept)} still failed.\n")

import argparse
import json
from datetime import datetime
from app.poster import post_payload, _log_status, FAILED_FILE

def load_failed_lines(path):
    items = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    items.append(obj)
                except json.JSONDecodeError:
                    _log_status("RETRY ERROR", {"reportId": "N/A"}, "Invalid JSON in failed.jsonl", code=None)
    except FileNotFoundError:
        pass
    return items

def save_failed_lines(path, items):
    with open(path, "w") as f:
        for obj in items:
            f.write(json.dumps(obj) + "\n")

def get_wrapped(obj):
    """Return (wrapper, payload_dict_ref). If wrapper has 'payload', give its ref.
       Else treat the wrapper itself as payload for backward compatibility."""
    if isinstance(obj, dict) and "payload" in obj and isinstance(obj["payload"], dict):
        return obj, obj["payload"]
    return obj, obj  # compat

def ensure_meta(wrapper):
    """Ensure wrapper carries retry_count, first_seen, last_error (without touching payload)."""
    if "retry_count" not in wrapper:
        wrapper["retry_count"] = 0
    if "first_seen" not in wrapper:
        wrapper["first_seen"] = datetime.utcnow().isoformat()
    if "last_error" not in wrapper:
        wrapper["last_error"] = ""
    return wrapper

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="endpoint to post to (e.g., http://localhost:8000/test-post)")
    ap.add_argument("--max", type=int, default=3, help="max retries per payload this run")
    ap.add_argument("--strip-trigger-fail", action="store_true",
                    help="remove triggerFail from payloads before retry (useful for demos)")
    args = ap.parse_args()

    items = load_failed_lines(FAILED_FILE)
    kept = []

    for obj in items:
        wrapper, payload = get_wrapped(obj)
        wrapper = ensure_meta(wrapper)

        # Respect max per-run retries
        if wrapper["retry_count"] >= args.max:
            kept.append(wrapper)
            continue

        # Optional cleanup of simulation flag for this retry run
        if args.strip_trigger_fail:
            payload.pop("triggerFail", None)

        # Perform retry
        res = post_payload(payload, args.url)

        if res["status"] == "success":
            _log_status("RETRY SUCCESS", payload, "OK", code=res.get("code", 200))
            continue  # Don't keep successful payloads

        # Failed or error → update metadata and keep
        wrapper["retry_count"] += 1
        wrapper["last_error"] = res.get("error", "Unknown error")
        _log_status("RETRY FAILURE", payload, wrapper["last_error"], code=res.get("code"))

        kept.append(wrapper)

    save_failed_lines(FAILED_FILE, kept)
    print(f"\nRetry complete. {len(kept)} still failed.\n")
