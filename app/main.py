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


from app.etl import clean_dataframe
from app.json_generator import generate_json_records


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
                "preview": text[:500]
            }
        else:
            return {"error": "Unsupported file format. Use .csv, .json, .xlsx or .pdf"}

        
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
        # Load file
        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file format"}

        # Clean it using ETL logic
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

@app.post("/download-json")
async def download_json(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()

    try:
        # Step 1: Load the file
        if filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode()))
        elif filename.endswith(".json"):
            df = pd.read_json(StringIO(content.decode()))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file format. Use .csv, .json, .xlsx"}

        # Step 2: Clean and transform
        df = clean_dataframe(df)
        json_output = generate_json_records(df)

        # Step 3: Return downloadable file
        json_bytes = json.dumps(json_output, indent=2).encode("utf-8")
        download_filename = filename.rsplit(".", 1)[0] + "_converted.json"
        return StreamingResponse(BytesIO(json_bytes), media_type="application/json", headers={
            "Content-Disposition": f"attachment; filename={download_filename}"
        })

    except Exception as e:
        return {"error": str(e)}