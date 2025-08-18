from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd
from app.poster import post_payload

router = APIRouter()

@router.post("/upload-csv", summary="Upload CSV or Excel file and auto-send to /test-post")
async def upload_csv(file: UploadFile = File(...)):
    filename = file.filename.lower()

    # Check file extension
    if filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        raise HTTPException(status_code=400, detail="Only .csv or .xlsx files are supported.")

    results = []

    for _, row in df.iterrows():
        payload = row.to_dict()
        result = post_payload(payload, url="http://127.0.0.1:8000/test-post")  # or Render URL
        results.append({
            "reportId": payload.get("reportId", "<missing>"),
            "status": result["status"],
            "code": result.get("code"),
            "error": result.get("error")
        })

    return {"processed": len(results), "results": results}