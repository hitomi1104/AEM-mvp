# # app/main.py
# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "LSMV Downstream MVP is live!"}



from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import StringIO, BytesIO
import pdfplumber
from app.parse_e2b_xml import parse_e2b_xml


from app.etl import clean_dataframe
from app.json_generator import generate_json_records
from app.utils import mask_json_values


app = FastAPI()

@app.get("/")
def root():
    return {"message": "LSMV Downstream MVP is live!"}



from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import StringIO, BytesIO
import pdfplumber
from app.etl import clean_dataframe  # ✅ make sure this import is here

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LSMV Downstream MVP is live!"}



@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        # Handle PDF early
        if filename.endswith(".pdf"):
            text = ""
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return {
                "filename": filename,
                "type": "pdf",
                "preview": text[:500]
            }

        # Handle XML early
        if filename.endswith(".xml"):
            records = parse_e2b_xml(content)
            return {
                "filename": filename,
                "records": records
            }

        # Handle tabular files
        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file format. Use .csv, .json, .xlsx, .xml, or .pdf"}

        df = clean_dataframe(df)

        return {
            "filename": filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(1).to_dict(orient="records")[0] if not df.empty else {}
        }

    except Exception as e:
        return {"error": str(e)}


from fastapi.responses import JSONResponse, StreamingResponse
import json

@app.post("/generate-json")
async def generate_json(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        # Handle XML separately
        if filename.endswith(".xml"):
            records = parse_e2b_xml(content)
            return {
                "filename": filename,
                "records": records
            }

        # Load tabular files
        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file format. Use .csv, .json, .xlsx, or .xml"}

        # Clean using ETL logic
        df = clean_dataframe(df)

        # Convert to DMP JSON structure
        json_output = generate_json_records(df)

        return {
            "filename": filename,
            "records": json_output
        }

    except Exception as e:
        return {"error": str(e)}
    



    
    from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import json



from fastapi.responses import StreamingResponse
import json

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
            return {"error": "Unsupported file format. Use .csv, .json, .xlsx, or .xml"}

        # Single place to generate the response
        json_bytes = json.dumps(records, indent=2).encode("utf-8")
        download_filename = filename.rsplit(".", 1)[0] + "_converted.json"

        return StreamingResponse(BytesIO(json_bytes), media_type="application/json", headers={
            "Content-Disposition": f"attachment; filename={download_filename}"
        })

    except Exception as e:
        return {"error": str(e)}
    

















    ######################### json-LSMV     #########################
from app.utils import mask_json_values
from fastapi.responses import JSONResponse
from fastapi import Request

@app.post("/generate-json-lsmv")
async def generate_json_lsmv(
    request: Request,
    file: UploadFile = File(None)
):
    try:
        if file is not None:
            # File was uploaded
            content = await file.read()
            original = json.loads(content.decode("utf-8"))
        else:
            # Raw JSON payload was sent
            original = await request.json()

        masked = mask_json_values(original)
        return JSONResponse(content=masked)

    except Exception as e:
        return {"error": str(e)}

# @app.post("/generate-json-lsmv")
# async def generate_json_lsmv(file: UploadFile = File(...)):
#     try:
#         content = await file.read()
#         original = json.loads(content.decode("utf-8"))
#         masked = mask_json_values(original)

#         return JSONResponse(content=masked)

#     except Exception as e:
#         return {"error": str(e)}
    
    #########################    
from app.poster import post_payload

import requests

def post_payload(payload, url="https://aem-mvp.onrender.com/generate-json-lsmv"):
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return True, response.status_code
        else:
            return False, response.status_code
    except requests.exceptions.RequestException as e:
        return False, str(e)
