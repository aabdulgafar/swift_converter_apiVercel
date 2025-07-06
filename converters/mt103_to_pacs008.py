import re
import xml.etree.ElementTree as ET

def convert_mt103_to_json(mt: str):
    result = {}
    blocks = re.findall(r":([0-9A-Z]{2,3}):(.*?)\r?\n", mt, re.DOTALL)
    for tag, value in blocks:
        result[tag.strip()] = value.strip()
    return {"type": "MT103", "fields": result}

def convert_json_to_pacs008(json_data: dict):
    fields = json_data.get("fields", {})
    root = ET.Element("pacs.008")
    credit = ET.SubElement(root, "CreditTransfer")

    if "20" in fields:
        ET.SubElement(credit, "TransactionReference").text = fields["20"]

    if "32A" in fields:
        date = fields["32A"][:6]
        currency = fields["32A"][6:9]
        amount = fields["32A"][9:]
        ET.SubElement(credit, "Date").text = date
        ET.SubElement(credit, "Currency").text = currency
        ET.SubElement(credit, "Amount").text = amount

    if "50K" in fields:
        ET.SubElement(credit, "OrderingCustomer").text = fields["50K"]

    if "59" in fields:
        ET.SubElement(credit, "Beneficiary").text = fields["59"]

    return ET.tostring(root, encoding="unicode")

def convert_mt103_to_pacs008(mt: str):
    json_data = convert_mt103_to_json(mt)
    return convert_json_to_pacs008(json_data)
