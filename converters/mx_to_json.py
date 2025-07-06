import xmltodict

def convert_mx_to_json(xml_string: str) -> dict:
    try:
        return xmltodict.parse(xml_string)
    except Exception as e:
        return {"error": str(e)}
