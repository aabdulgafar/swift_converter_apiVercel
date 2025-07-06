# import re
# import xml.etree.ElementTree as ET
# from datetime import datetime
#
# def extract_block(text, block_number):
#     match = re.search(rf"\{{{block_number}:(.*?)\}}", text, re.DOTALL)
#     return match.group(1).strip() if match else ""
#
# def convert_mt103_to_json(mt: str):
#     result = {}
#     blocks = re.findall(r":([0-9A-Z]{2,3}):(.*?)\n", mt, re.DOTALL)
#     for tag, value in blocks:
#         result[tag.strip()] = value.strip()
#     return {"type": "MT103", "fields": result}
#
# def convert_json_to_pacs008(json_data: dict):
#     # Placeholder for basic version
#     return "<pacs.008>Converted from JSON</pacs.008>"
#
# def convert_mt103_to_pacs008(mt: str):
#     json_data = convert_mt103_to_json(mt)
#     return convert_json_to_pacs008(json_data)
#
# def convert_full_mt103_to_json(mt: str):
#     block1 = extract_block(mt, 1)
#     block2 = extract_block(mt, 2)
#     block3 = extract_block(mt, 3)
#     block4 = extract_block(mt, 4)
#
#     fields = dict(re.findall(r":([0-9A-Z]{2,3}):(.*?)\n", block4 + "\n", re.DOTALL))
#     sender_bic = re.findall(r"F01(\w{8})", block1)
#     receiver_bic = re.findall(r"O103\d+(\w{8})", block2)
#     uetr = re.search(r"\{121:(.*?)\}", block3)
#
#     return {
#         "AppHdr": {
#             "Fr": sender_bic[0] if sender_bic else "",
#             "To": receiver_bic[0] if receiver_bic else "",
#             "BizMsgIdr": fields.get("20", "") + "-pacs008",
#             "MsgDefIdr": "pacs.008.001.08",
#             "BizSvc": "swift.cbprplus.02"
#         },
#         "Document": {
#             "InstrId": fields.get("20", ""),
#             "EndToEndId": fields.get("70", "").split("///ROC/")[-1].strip(),
#             "Amt": {
#                 "Instd": fields.get("33B", "")[3:] if "33B" in fields else "",
#                 "Sttlm": fields.get("32A", "")[9:] if "32A" in fields else ""
#             },
#             "Dbtr": fields.get("50F", "").split("\n")[0],
#             "Cdtr": fields.get("59", "").split("\n")[0],
#             "UETR": uetr.group(1) if uetr else ""
#         }
#     }
#
# def convert_full_mt103_to_pacs008(mt: str):
#     json_data = convert_full_mt103_to_json(mt)
#     doc = ET.Element("Document")
#     hdr = ET.SubElement(doc, "Header")
#     ET.SubElement(hdr, "Sender").text = json_data["AppHdr"]["Fr"]
#     ET.SubElement(hdr, "Receiver").text = json_data["AppHdr"]["To"]
#
#     body = ET.SubElement(doc, "Body")
#     ET.SubElement(body, "Amount").text = json_data["Document"]["Amt"]["Instd"]
#     ET.SubElement(body, "Currency").text = "EUR"
#
#     return ET.tostring(doc, encoding="unicode")
import re
import uuid
from datetime import datetime

def parse_mt103_blocks(message: str):
    match = re.search(r"\{4:\s*(.*?)-\}", message, re.DOTALL)
    if not match:
        return {}

    block4 = match.group(1)
    fields = {}

    for line in block4.split('\n'):
        line = line.strip()
        if line.startswith(":") and ":" in line[1:]:
            tag, value = line[1:].split(":", 1)
            fields[tag] = value.strip()
        else:
            if fields:
                last_tag = list(fields.keys())[-1]
                fields[last_tag] += " " + line.strip()

    return fields

def convert_mt103_to_json(message: str):
    fields = parse_mt103_blocks(message)
    return {
        "type": "MT103",
        "fields": fields
    }

def convert_mt103_to_pacs008(message: str):
    data = convert_mt103_to_json(message)
    fields = data["fields"]
    uetr = str(uuid.uuid4())
    now = datetime.now().isoformat()

    return f"""<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
    <head:Fr><head:FIId><head:FinInstnId><head:BICFI>{fields.get("52A", "")}</head:BICFI></head:FinInstnId></head:FIId></head:Fr>
    <head:To><head:FIId><head:FinInstnId><head:BICFI>{fields.get("57A", "")}</head:BICFI></head:FinInstnId></head:FIId></head:To>
    <head:BizMsgIdr>{fields.get("20", "")}</head:BizMsgIdr>
    <head:MsgDefIdr>pacs.008.001.08</head:MsgDefIdr>
    <head:BizSvc>swift.cbprplus.02</head:BizSvc>
    <head:CreDt>{now}</head:CreDt>
</head:AppHdr>
<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
    <pacs:FIToFICstmrCdtTrf>
        <pacs:GrpHdr>
            <pacs:MsgId>{fields.get("20", "")}</pacs:MsgId>
            <pacs:CreDtTm>{now}</pacs:CreDtTm>
            <pacs:NbOfTxs>1</pacs:NbOfTxs>
            <pacs:SttlmInf><pacs:SttlmMtd>INDA</pacs:SttlmMtd></pacs:SttlmInf>
        </pacs:GrpHdr>
        <pacs:CdtTrfTxInf>
            <pacs:PmtId>
                <pacs:InstrId>{fields.get("20", "")}</pacs:InstrId>
                <pacs:EndToEndId>{fields.get("70", "")}</pacs:EndToEndId>
                <pacs:UETR>{uetr}</pacs:UETR>
            </pacs:PmtId>
            <pacs:IntrBkSttlmAmt Ccy="EUR">{fields.get("32A", "0").split('EUR')[-1].replace(',', '.')}</pacs:IntrBkSttlmAmt>
            <pacs:IntrBkSttlmDt>{fields.get("32A", "")[:6]}</pacs:IntrBkSttlmDt>
            <pacs:ChrgBr>DEBT</pacs:ChrgBr>
            <pacs:InstgAgt><pacs:FinInstnId><pacs:BICFI>{fields.get("52A", "")}</pacs:BICFI></pacs:FinInstnId></pacs:InstgAgt>
            <pacs:InstdAgt><pacs:FinInstnId><pacs:BICFI>{fields.get("57A", "")}</pacs:BICFI></pacs:FinInstnId></pacs:InstdAgt>
            <pacs:Dbtr><pacs:Nm>{fields.get("50F", "").splitlines()[0]}</pacs:Nm></pacs:Dbtr>
            <pacs:Cdtr><pacs:Nm>{fields.get("59", "").splitlines()[0]}</pacs:Nm></pacs:Cdtr>
            <pacs:RmtInf><pacs:Ustrd>{fields.get("70", "")}</pacs:Ustrd></pacs:RmtInf>
        </pacs:CdtTrfTxInf>
    </pacs:FIToFICstmrCdtTrf>
</pacs:Document>"""
