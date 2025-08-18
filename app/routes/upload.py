from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd

from app.utils import mask_json_values
from app.poster import _log_status, _save_failed_payload

router = APIRouter()


@router.post("/upload-csv", summary="Upload CSV or Excel file and auto-send to /test-post logic")
async def upload_csv(file: UploadFile = File(...)):
    filename = file.filename.lower()

    # Read file based on extension
    if filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        raise HTTPException(status_code=400, detail="Only .csv or .xlsx files are supported.")

    results = []

    for _, row in df.iterrows():
        payload = row.to_dict()
        masked_payload = mask_json_values(payload)

        if payload.get("triggerFail") is True:
            _log_status("FAILURE", masked_payload, "Simulated failure via triggerFail", code=500)
            _save_failed_payload(payload)
            results.append({
                "reportId": payload.get("reportId", "<missing>"),
                "status": "error",
                "code": 500,
                "error": "Simulated failure via triggerFail"
            })
        else:
            _log_status("SUCCESS", masked_payload, "OK", code=200)
            results.append({
                "reportId": payload.get("reportId", "<missing>"),
                "status": "success",
                "code": 200
            })

    return {"processed": len(results), "results": results}