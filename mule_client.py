# LSVM_CLIENT_ID=a3f160dbec5546a0b322a345857974e5
# LSVM_CLIENT_SECRET=86bedb6024624ABDB426b1b633d7De0d

# MULE_CLIENT_ID=9dbbeca619cc4949bbdc62aec9a38148
# MULE_CLIENT_SECRET=7915a327336b42888C48d0CF6C6fc86F

# MULE_HEALTHCHECK_URL=https://cdrh-dt-eip.dev.fda.gov/emdr/healthcheck
# MULE_POST_URL=https://cdrh-dt-eip.dev.fda.gov/emdr/init_supp
# MULE_PATCH_URL=https://cdrh-dt-eip.dev.fda.gov/emdr/narratives
# MULE_RUN_YN=Y
# MULE_RUN_INTERVAL_MINUTES=1

# mule_client.py
# NOTE: for quick testing you left real IDs here; move to env vars later.

import os, requests, json

MULE_HEALTH_URL = "https://cdrh-dt-eip.dev.fda.gov/emdr/healthcheck"
MULE_POST_URL   = "https://cdrh-dt-eip.dev.fda.gov/emdr/init_supp"
MULE_PATCH_URL  = "https://cdrh-dt-eip.dev.fda.gov/emdr/narratives"

# TEMP for local testing; remove defaults later and use env vars.
MULE_CLIENT_ID     = os.getenv("MULE_CLIENT_ID", "9dbbeca619cc4949bbdc62aec9a38148")
MULE_CLIENT_SECRET = os.getenv("MULE_CLIENT_SECRET", "7915a327336b42888C48d0CF6C6fc86F")

def _auth_headers():
    return {
        "x-client-id": MULE_CLIENT_ID,
        "x-client-secret": MULE_CLIENT_SECRET,
        "Content-Type": "application/json",
    }

def mule_health():
    r = requests.get(MULE_HEALTH_URL, headers=_auth_headers(), timeout=15)
    return {"code": r.status_code, "body": r.text}

def mule_post(payload: dict):
    r = requests.post(MULE_POST_URL, headers=_auth_headers(),
                      data=json.dumps(payload), timeout=30)
    return {"code": r.status_code, "body": r.text}

def mule_patch(payload: dict):
    r = requests.patch(MULE_PATCH_URL, headers=_auth_headers(),
                       data=json.dumps(payload), timeout=30)
    return {"code": r.status_code, "body": r.text}

if __name__ == "__main__":
    # ad‑hoc local test (runs only when you `python mule_client.py`)
    print("Health:", mule_health())
    print("POST:", mule_post({"reportId":"AEV-MULE-TEST-001","eventDate":"2025-08-21"}))
