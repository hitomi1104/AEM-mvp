import json
import os
from app.poster import submit_with_logging

FAILED_FILE = "failed.jsonl"
NEW_FAILED_FILE = "failed_tmp.jsonl"
TARGET_URL = "https://aem-mvp.onrender.com/test-post"
RETRY_LIMIT = 3

retry_failures = []

with open(FAILED_FILE, "r") as f:
    lines = f.readlines()

for line in lines:
    try:
        payload = json.loads(line)
        retry_count = payload.get("retry_count", 1)

        if retry_count >= RETRY_LIMIT:
            retry_failures.append(payload)
            continue

        result = submit_with_logging(payload, TARGET_URL)

        if result["status"] != "success":
            payload["retry_count"] = retry_count + 1
            retry_failures.append(payload)

    except Exception as e:
        print("Retry error:", str(e))

# Write updated failed list back
with open(NEW_FAILED_FILE, "w") as f:
    for p in retry_failures:
        f.write(json.dumps(p) + "\n")

# Replace old file
os.replace(NEW_FAILED_FILE, FAILED_FILE)

print(f"\nRetry complete. {len(retry_failures)} still failed.\n")


from app.poster import retry_failed_payloads

# Point at Render or local, either works:
URL = "https://aem-mvp.onrender.com/test-post"  # or "http://localhost:8000/test-post"
retry_failed_payloads(URL)


