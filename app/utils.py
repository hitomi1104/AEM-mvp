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