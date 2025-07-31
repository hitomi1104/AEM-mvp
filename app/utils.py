def mask_json_values(data):
    """
    Recursively replaces all values in a JSON-like dict or list with "1"
    """
    if isinstance(data, dict):
        return {key: mask_json_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [mask_json_values(item) for item in data]
    else:
        return "1"