def to_dmp_json(row: dict) -> dict:
    return {
        "reportId": row.get("report_id"),
        "eventDate": row.get("event_date"),
        "description": row.get("description"),
        "product": row.get("suspect_product_name"),
        "dose": row.get("dose"),
        "route": row.get("route"),
        "outcome": row.get("outcome"),
        "source": row.get("report_source")[0] if isinstance(row.get("report_source"), list) else row.get("report_source")
    }

def generate_json_records(df):
    return [to_dmp_json(row) for row in df.to_dict(orient="records")]