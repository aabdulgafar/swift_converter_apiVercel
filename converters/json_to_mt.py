def convert_json_to_mt(data: dict) -> str:
    # Reconstruct MT message from simple jsonMT
    mt = ""
    for key in sorted(data.keys()):
        mt += f"{{{key}:{data[key]}}}"
    return mt
