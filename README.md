# 🧪 LSMV Downstream Integration MVP (FastAPI)

## Overview

This MVP simulates a lightweight downstream processing system for FDA 3500A adverse event reports using **FastAPI**.

It demonstrates:
- Intake of mock FDA 3500A data (CSV/JSON)
- ETL transformation of structured data
- JSON conversion for downstream systems (e.g., DMP)
- AE pattern analysis (e.g., severity, product trends)
- (Optional) Excel merging for HFCS public reports

---

## 🛠️ Tech Stack

- **FastAPI**: API framework
- **Pandas**: ETL and data manipulation
- **Uvicorn**: ASGI server
- **JSON / Excel**: Output formats
- **Faker**: Synthetic data generation

---

## 📁 Project Structure

```
lsmv-downstream-fastapi/
│
├── app/
│   ├── main.py                # FastAPI app entrypoint
│   ├── etl.py                 # ETL: clean & transform data
│   ├── json_generator.py      # Converts records to JSON
│   ├── scoring.py             # (Optional) Basic AE scoring logic
│   ├── merger.py              # (Optional) Excel merger for HFCS
│   └── models.py              # Pydantic models for validation
│
├── data/
│   ├── mock_fda_3500A_data.csv
│   ├── mock_fda_3500A_data.json
│   └── historical_primo_data.xlsx  # For HFCS merger
│
├── tests/
│   └── test_endpoints.py      # Unit/API tests
│
├── requirements.txt
├── README.md
└── .env (optional)
```

---

## 🔄 API Endpoints

### `POST /upload`
Upload a CSV/JSON file of FDA 3500A reports.

- Accepts: `.csv` or `.json`
- Returns: Parsed metadata summary (count, fields)

---

### `POST /generate-json`
Transforms input reports into structured JSON objects for DMP downstream use.

- Accepts: In-memory or uploaded records
- Returns: List of JSON files

---

### `GET /score`
(Optional) Computes AE frequencies, outcomes, or basic EBGM proxy logic.

---

### `POST /merge-excel`
(Optional) Combines historical Primo Excel data + new LSMV records.

---

## 🧪 Example Use Case

```bash
curl -X POST "http://localhost:8000/upload" \
     -F "file=@data/mock_fda_3500A_data.csv"
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run API Locally

```bash
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000/docs` for Swagger UI

---

## 📌 Next Steps

- Add authentication (optional)
- Support more advanced EBGM scoring
- Auto-schedule report generation
- Upload to S3, push to Mulesoft, etc.

---

## 👩‍💻 Author

**Hitomi Hoshino** – AI Engineer  
FDA HFP | LSMV | AEM | DMP JSON | Downstream Integrations
