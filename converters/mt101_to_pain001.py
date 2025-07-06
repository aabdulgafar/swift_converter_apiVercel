import re
import xml.etree.ElementTree as ET

def convert_mt101_to_json(mt: str):
    result = {}
    blocks = re.findall(r":([0-9A-Z]{2,3}):(.*?)\r?\n", mt, re.DOTALL)
    for tag, value in blocks:
        result[tag.strip()] = value.strip()
    return {"type": "MT101", "fields": result}

def convert_json_to_pain001(json_data: dict):
    fields = json_data.get("fields", {})
    root = ET.Element("pain.001")
    payment = ET.SubElement(root, "PaymentInstruction")

    if "20" in fields:
        ET.SubElement(payment, "TransactionReference").text = fields["20"]

    if "32B" in fields:
        currency, amount = fields["32B"][:3], fields["32B"][3:]
        ET.SubElement(payment, "Currency").text = currency
        ET.SubElement(payment, "Amount").text = amount

    return ET.tostring(root, encoding="unicode")

def convert_mt101_to_pain001(mt: str):
    json_data = convert_mt101_to_json(mt)
    return convert_json_to_pain001(json_data)
