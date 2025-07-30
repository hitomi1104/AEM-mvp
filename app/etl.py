import pandas as pd
import ast

REQUIRED_FIELDS = [
    "report_id", "event_date", "report_type", "outcome",
    "description", "suspect_product_name", "route"
]

def safe_eval(val):
    try:
        if isinstance(val, str) and val.strip().startswith("[") and val.strip().endswith("]"):
            return ast.literal_eval(val)
    except:
        pass
    return val

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df = df.dropna(axis=1, how="all")
    df = df.dropna(subset=REQUIRED_FIELDS)

    list_fields = ["report_type", "outcome", "race", "report_source"]
    for col in list_fields:
        if col in df.columns:
            df[col] = df[col].map(safe_eval)

    return df