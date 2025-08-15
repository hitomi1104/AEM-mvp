# def mask_json_values(data):
#     """
#     Recursively replaces all values in a JSON-like dict or list with "1"
#     """
#     if isinstance(data, dict):
#         return {key: mask_json_values(value) for key, value in data.items()}
#     elif isinstance(data, list):
#         return [mask_json_values(item) for item in data]
#     else:
#         return "1"

def mask_json_values(obj):
    """
    Placeholder “masking”: transforms every leaf value to "1".
    Keeps the same keys/shape for downstream testing.
    """
    if isinstance(obj, dict):
        return {k: mask_json_values(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [mask_json_values(v) for v in obj]
    return "1"