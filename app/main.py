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

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LSMV Downstream MVP is live!"}

@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        elif filename.endswith(".pdf"):
            text = ""
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return {
                "filename": filename,
                "type": "pdf",
                "preview": text[:500]  # first 500 chars of extracted text
            }
        else:
            return {"error": "Unsupported file format. Use .csv, .json, .xlsx or .pdf"}

        return {
            "filename": filename,
            "rows": len(df),
            "columns": list(df.columns),
        }

    except Exception as e:
        return {"error": str(e)}