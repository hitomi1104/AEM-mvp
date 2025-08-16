# app/main.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import json

from app.utils import mask_json_values
from app.poster import _log_status, _save_failed_payload

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LSMV Downstream MVP is live!"}

@app.post("/test-post")
async def test_post(request: Request, file: UploadFile = File(None)):
    try:
        # 1) Ingest payload (JSON body or multipart file)
        if file:
            content = await file.read()
            payload = json.loads(content.decode("utf-8"))
        else:
            payload = await request.json()

        # 2) Simulate failure when asked
        if payload.get("triggerFail") is True:
            _log_status("FAILURE", payload, "Simulated failure via triggerFail → Code 500")
            _save_failed_payload(payload)
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": "Simulated failure via triggerFail"},
            )

        # 3) Mask values (POC behavior only)
        masked = mask_json_values(payload)

        # 4) Log success (Code 200)
        _log_status("SUCCESS", payload, "OK", code=200)
        return JSONResponse(content=masked, status_code=200)

    except Exception as e:
        # Fallback failure logging
        try:
            payload
        except NameError:
            payload = {"reportId": "N/A"}
        _log_status("FAILURE", payload, f"{str(e)} → Code 500")
        _save_failed_payload(payload)
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})