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

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LSMV Downstream MVP is live!"}


@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        # Handle PDF
        if filename.endswith(".pdf"):
            text = ""
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return {"filename": filename, "type": "pdf", "preview": text[:500]}

        # Handle XML
        if filename.endswith(".xml"):
            records = parse_e2b_xml(content)
            return {"filename": filename, "records": records}

        # Handle tabular files
        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file format"}

        df = clean_dataframe(df)
        return {
            "filename": filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(1).to_dict(orient="records")[0] if not df.empty else {}
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/generate-json")
async def generate_json(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        if filename.endswith(".xml"):
            records = parse_e2b_xml(content)
            return {"filename": filename, "records": records}

        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file format"}

        df = clean_dataframe(df)
        json_output = generate_json_records(df)

        return {"filename": filename, "records": json_output}

    except Exception as e:
        return {"error": str(e)}


@app.post("/download-json")
async def download_json(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        if filename.endswith(".xml"):
            records = parse_e2b_xml(content)
        elif filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
            df = clean_dataframe(df)
            records = generate_json_records(df)
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
            df = clean_dataframe(df)
            records = generate_json_records(df)
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
            df = clean_dataframe(df)
            records = generate_json_records(df)
        else:
            return {"error": "Unsupported file format"}

        json_bytes = json.dumps(records, indent=2).encode("utf-8")
        download_filename = filename.rsplit(".", 1)[0] + "_converted.json"

        return StreamingResponse(BytesIO(json_bytes), media_type="application/json", headers={
            "Content-Disposition": f"attachment; filename={download_filename}"
        })

    except Exception as e:
        return {"error": str(e)}


# @app.post("/generate-json-lsmv")
# # async def generate_json_lsmv(request: Request, file: UploadFile = File(None)):
# async def generate_json_lsmv(request: Request):
#     try:
#         if file is not None:
#             content = await file.read()
#             original = json.loads(content.decode("utf-8"))
#         else:
#             original = await request.json()

#         masked = mask_json_values(original)
#         return JSONResponse(content=masked)

#     except Exception as e:
#         return {"error": str(e)}




@app.post("/generate-json-lsmv")
async def generate_json_lsmv(request: Request, file: UploadFile = File(None)):
    try:
        if file:
            content = await file.read()
            original = json.loads(content.decode("utf-8"))
        else:
            original = await request.json()

        masked = mask_json_values(original)
        return JSONResponse(content=masked)

    except Exception as e:
        return {"error": str(e)}

    
# @app.post("/test-post")
# async def test_post(request: Request, file: UploadFile = File(None)):
#     try:
#         if file:
#             content = await file.read()
#             payload = json.loads(content.decode("utf-8"))
#         else:
#             payload = await request.json()

#         # Testing fail scenario
#         if str(payload.get("triggerFail")).lower() in ["true", "1", "yes"]:
#             raise ValueError("Simulated failure for testing")

#         masked = mask_json_values(payload)
#         return JSONResponse(content=masked)

#     except Exception as e:
#         return {"status": "error", "error": str(e)}

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
        from app.utils import mask_json_values
        masked = mask_json_values(payload)

        # Step 4: Log success
        from app.poster import _log_status
        _log_status("SUCCESS", payload, "Code 200")

        return JSONResponse(content=masked)

    except Exception as e:
        # Step 5: Log failure + save for retry
        from app.poster import _log_status, _save_failed_payload
        payload = locals().get("payload", {})  # fallback if payload isn't available
        _log_status("FAILURE", payload, str(e))
        _save_failed_payload(payload)
        return {"status": "error", "error": str(e)}
    





from app.poster import post_payload, _log_status, _save_failed_payload
def submit_with_logging(payload, url):
    result = post_payload(payload, url)
    if result["status"] == "success":
        _log_status("SUCCESS", payload, result["response"])
    else:
        _log_status("FAILED", payload, result.get("error", "Unknown error"))
        _save_failed_payload(payload)
    return result