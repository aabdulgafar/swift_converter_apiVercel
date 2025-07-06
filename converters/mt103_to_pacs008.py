import re
import xml.etree.ElementTree as ET
from datetime import datetime

def extract_block(text, block_number):
    match = re.search(rf"\{{{block_number}:(.*?)\}}", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def convert_mt103_to_json(mt: str):
    result = {}
    blocks = re.findall(r":([0-9A-Z]{2,3}):(.*?)\n", mt, re.DOTALL)
    for tag, value in blocks:
        result[tag.strip()] = value.strip()
    return {"type": "MT103", "fields": result}

def convert_json_to_pacs008(json_data: dict):
    # Placeholder for basic version
    return "<pacs.008>Converted from JSON</pacs.008>"

def convert_mt103_to_pacs008(mt: str):
    json_data = convert_mt103_to_json(mt)
    return convert_json_to_pacs008(json_data)

def convert_full_mt103_to_json(mt: str):
    block1 = extract_block(mt, 1)
    block2 = extract_block(mt, 2)
    block3 = extract_block(mt, 3)
    block4 = extract_block(mt, 4)

    fields = dict(re.findall(r":([0-9A-Z]{2,3}):(.*?)\n", block4 + "\n", re.DOTALL))
    sender_bic = re.findall(r"F01(\w{8})", block1)
    receiver_bic = re.findall(r"O103\d+(\w{8})", block2)
    uetr = re.search(r"\{121:(.*?)\}", block3)

    return {
        "AppHdr": {
            "Fr": sender_bic[0] if sender_bic else "",
            "To": receiver_bic[0] if receiver_bic else "",
            "BizMsgIdr": fields.get("20", "") + "-pacs008",
            "MsgDefIdr": "pacs.008.001.08",
            "BizSvc": "swift.cbprplus.02"
        },
        "Document": {
            "InstrId": fields.get("20", ""),
            "EndToEndId": fields.get("70", "").split("///ROC/")[-1].strip(),
            "Amt": {
                "Instd": fields.get("33B", "")[3:] if "33B" in fields else "",
                "Sttlm": fields.get("32A", "")[9:] if "32A" in fields else ""
            },
            "Dbtr": fields.get("50F", "").split("\n")[0],
            "Cdtr": fields.get("59", "").split("\n")[0],
            "UETR": uetr.group(1) if uetr else ""
        }
    }

def convert_full_mt103_to_pacs008(mt: str):
    json_data = convert_full_mt103_to_json(mt)
    doc = ET.Element("Document")
    hdr = ET.SubElement(doc, "Header")
    ET.SubElement(hdr, "Sender").text = json_data["AppHdr"]["Fr"]
    ET.SubElement(hdr, "Receiver").text = json_data["AppHdr"]["To"]

    body = ET.SubElement(doc, "Body")
    ET.SubElement(body, "Amount").text = json_data["Document"]["Amt"]["Instd"]
    ET.SubElement(body, "Currency").text = "EUR"

    return ET.tostring(doc, encoding="unicode")
