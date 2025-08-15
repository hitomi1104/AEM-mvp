from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import pdfplumber
import json
from io import StringIO, BytesIO
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File

from app.etl import clean_dataframe
from app.json_generator import generate_json_records
from app.parse_e2b_xml import parse_e2b_xml
from app.utils import mask_json_values
from app.poster import post_payload

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import json

from app.utils import mask_json_values
from app.poster import post_payload, _log_status, _save_failed_payload

app = FastAPI()


@app.get("/")
def root():
    return {"message": "LSMV Downstream MVP is live!"}


@app.post("/test-post")
async def test_post(request: Request, file: UploadFile = File(None)):
    try:
        # Step 1: Load payload from file or JSON
        if file:
            content = await file.read()
            payload = json.loads(content.decode("utf-8"))
        else:
            payload = await request.json()

        # Step 2: Simulate failure if requested
        if payload.get("triggerFail") is True:
            raise ValueError("Simulated failure via triggerFail")

        # Step 3: Mask values
        masked = mask_json_values(payload)

        # Step 4: Log success
        _log_status("SUCCESS", payload, "Code 200")

        return JSONResponse(content=masked)

    except Exception as e:
        # Step 5: Log failure + save for retry
        payload = locals().get("payload", {})  # fallback if payload isn't available
        _log_status("FAILURE", payload, str(e))
        _save_failed_payload(payload)
        return {"status": "error", "error": str(e)}



# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "LSMV Downstream MVP is live!"}



# @app.post("/generate-json-lsmv")
# async def generate_json_lsmv(request: Request, file: UploadFile = File(None)):
#     try:
#         if file:
#             content = await file.read()
#             original = json.loads(content.decode("utf-8"))
#         else:
#             original = await request.json()

#         masked = mask_json_values(original)
#         return JSONResponse(content=masked)

#     except Exception as e:
#         return {"error": str(e)}

    


# @app.post("/test-post")
# async def test_post(request: Request, file: UploadFile = File(None)):
#     try:
#         # Step 1: Load payload from file or JSON
#         if file:
#             content = await file.read()
#             payload = json.loads(content.decode("utf-8"))
#         else:
#             payload = await request.json()

#         # Step 2: Simulate failure if requested
#         if payload.get("triggerFail") is True:
#             raise ValueError("Simulated failure via triggerFail")

#         # Step 3: Mask values
#         from app.utils import mask_json_values
#         masked = mask_json_values(payload)

#         # Step 4: Log success
#         from app.poster import _log_status
#         _log_status("SUCCESS", payload, "Code 200")

#         return JSONResponse(content=masked)

#     except Exception as e:
#         # Step 5: Log failure + save for retry
#         from app.poster import _log_status, _save_failed_payload
#         payload = locals().get("payload", {})  # fallback if payload isn't available
#         _log_status("FAILURE", payload, str(e))
#         _save_failed_payload(payload)
#         return {"status": "error", "error": str(e)}
    





# from app.poster import post_payload, _log_status, _save_failed_payload
# def submit_with_logging(payload, url):
#     result = post_payload(payload, url)
#     if result["status"] == "success":
#         _log_status("SUCCESS", payload, result["response"])
#     else:
#         _log_status("FAILED", payload, result.get("error", "Unknown error"))
#         _save_failed_payload(payload)
#     return result