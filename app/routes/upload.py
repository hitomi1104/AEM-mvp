from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd

from app.poster import _log_status, _save_failed_payload
from app.utils import mask_json_values

router = APIRouter()


def is_truthy(value):
    """Check if value represents a 'true' boolean"""
    return str(value).strip().lower() in ("true", "1", "yes")


def process_payload_direct(payload):
    """Direct version of /test-post logic — no HTTP calls"""
    rid = str(payload.get("reportId", "<missing>"))
    masked = mask_json_values(payload)

    if is_truthy(payload.get("triggerFail")):
        _log_status("FAILURE", {"reportId": rid}, "Simulated failure via triggerFail", code=500)
        _save_failed_payload(payload)
        return {
            "status": "error",
            "code": 500,
            "error": "Simulated failure via triggerFail"
        }
    else:
        _log_status("SUCCESS", {"reportId": rid}, "OK", code=200)
        return {
            "status": "success",
            "code": 200
        }


@router.post("/upload-csv", summary="Upload CSV or Excel file and auto-send to /test-post logic")
async def upload_csv(file: UploadFile = File(...)):
    filename = file.filename.lower()

    # Read file, force all columns as string
    if filename.endswith(".csv"):
        df = pd.read_csv(file.file, dtype=str)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file.file, dtype=str)
    else:
        raise HTTPException(status_code=400, detail="Only .csv or .xlsx files are supported.")

    results = []

    for _, row in df.iterrows():
        payload = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.to_dict().items()}
        payload["reportId"] = str(payload.get("reportId", "<missing>")).strip()

        result = process_payload_direct(payload)

        results.append({
            "reportId": payload.get("reportId", "<missing>"),
            "status": result["status"],
            "code": result.get("code"),
            "error": result.get("error")
        })

    return {"processed": len(results), "results": results}