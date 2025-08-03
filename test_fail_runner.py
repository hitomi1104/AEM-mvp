from app.poster import submit_with_logging

# Simulated failing payload
payload = {
    "reportId": "AEV-TEST-FAIL-001",
    "triggerFail": True
}
url = "https://aem-mvp.onrender.com/test-post"

# Submit via your logging system
result = submit_with_logging(payload, url)

print("Result:", result)
