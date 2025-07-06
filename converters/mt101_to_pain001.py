# import re
# import xml.etree.ElementTree as ET
# from datetime import datetime
#
# def extract_block(text, block_number):
#     match = re.search(rf"\{{{block_number}:(.*?)\}}", text, re.DOTALL)
#     return match.group(1).strip() if match else ""
#
# def convert_mt101_to_json(mt: str):
#     result = {}
#     blocks = re.findall(r":([0-9A-Z]{2,3}):(.*?)\n", mt, re.DOTALL)
#     for tag, value in blocks:
#         result[tag.strip()] = value.strip()
#     return {"type": "MT101", "fields": result}
#
# def convert_json_to_pain001(json_data: dict):
#     # Placeholder for basic version
#     return "<pain.001>Converted from JSON</pain.001>"
#
# def convert_mt101_to_pain001(mt: str):
#     json_data = convert_mt101_to_json(mt)
#     return convert_json_to_pain001(json_data)
#
# def convert_full_mt101_to_json(mt: str):
#     block1 = extract_block(mt, 1)
#     block2 = extract_block(mt, 2)
#     block3 = extract_block(mt, 3)
#     block4 = extract_block(mt, 4)
#     block5 = extract_block(mt, 5)
#
#     fields = dict(re.findall(r":([0-9A-Z]{2,3}):(.*?)\n", block4 + "\n", re.DOTALL))
#
#     sender_bic = re.findall(r"F01(\w{8})", block1)
#     receiver_bic = re.findall(r"O101\d+(\w{8})", block2)
#     uetr = re.search(r"\{121:(.*?)\}", block3)
#     end_to_end_id = fields.get("70", "").split("///ROC/")[-1].split("\n")[0].strip()
#
#     return {
#         "AppHdr": {
#             "Fr": sender_bic[0] if sender_bic else "",
#             "To": receiver_bic[0] if receiver_bic else "",
#             "BizMsgIdr": fields.get("20", "") + "-pain001",
#             "MsgDefIdr": "pain.001.001.09",
#             "BizSvc": "swift.scoreplus.01"
#         },
#         "Document": {
#             "PmtInfId": fields.get("21", ""),
#             "Amt": {
#                 "Ccy": fields.get("32B", "")[:3],
#                 "Value": fields.get("32B", "")[3:]
#             },
#             "Dbtr": fields.get("50F", "").split("\n")[0],
#             "Cdtr": fields.get("59", "").split("\n")[0],
#             "EndToEndId": end_to_end_id,
#             "UETR": uetr.group(1) if uetr else ""
#         }
#     }
#
# def convert_full_mt101_to_pain001(mt: str):
#     # Simplified version of XML generation for demo purposes
#     json_data = convert_full_mt101_to_json(mt)
#     doc = ET.Element("Document")
#     hdr = ET.SubElement(doc, "Header")
#     ET.SubElement(hdr, "Sender").text = json_data["AppHdr"]["Fr"]
#     ET.SubElement(hdr, "Receiver").text = json_data["AppHdr"]["To"]
#
#     body = ET.SubElement(doc, "Body")
#     ET.SubElement(body, "Amount").text = json_data["Document"]["Amt"]["Value"]
#     ET.SubElement(body, "Currency").text = json_data["Document"]["Amt"]["Ccy"]
#
#     return ET.tostring(doc, encoding="unicode")
import re
import uuid
from datetime import datetime

def parse_mt101_blocks(message: str):
    # Extract the {4: block
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

def convert_mt101_to_json(message: str):
    fields = parse_mt101_blocks(message)
    return {
        "type": "MT101",
        "fields": fields
    }

def convert_mt101_to_pain001(message: str):
    data = convert_mt101_to_json(message)
    fields = data["fields"]
    uetr = str(uuid.uuid4())
    now = datetime.now().isoformat()

    return f"""<AppHdr xmlns="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
    <Fr><OrgId><Id><OrgId><AnyBIC>{fields.get("50C", "")}</AnyBIC></OrgId></Id></OrgId></Fr>
    <To><FIId><FinInstnId><BICFI>{fields.get("52A", "")}</BICFI></FinInstnId></FIId></To>
    <BizMsgIdr>{fields.get("20", "")}</BizMsgIdr>
    <MsgDefIdr>pain.001.001.09</MsgDefIdr>
    <BizSvc>swift.scoreplus.01</BizSvc>
    <CreDt>{now}</CreDt>
</AppHdr>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>{fields.get("20", "")}</MsgId>
            <CreDtTm>{now}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <InitgPty>
                <Id><OrgId><AnyBIC>{fields.get("50C", "")}</AnyBIC></OrgId></Id>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>{fields.get("21", "")}</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <ReqdExctnDt><Dt>{fields.get("30", "")}</Dt></ReqdExctnDt>
            <Dbtr><Nm>{fields.get("50F", "").splitlines()[0]}</Nm></Dbtr>
            <DbtrAcct><Id><Othr><Id>{fields.get("50F", "").splitlines()[0]}</Id></Othr></Id></DbtrAcct>
            <DbtrAgt><FinInstnId><BICFI>{fields.get("52A", "")}</BICFI></FinInstnId></DbtrAgt>
            <CdtTrfTxInf>
                <PmtId><EndToEndId>{fields.get("70", "")}</EndToEndId><UETR>{uetr}</UETR></PmtId>
                <Amt><EqvtAmt><Amt Ccy="EUR">{fields.get("33B", "0").replace(',', '.')}</Amt><CcyOfTrf>{fields.get("32B", "EUR")[:3]}</CcyOfTrf></EqvtAmt></Amt>
                <ChrgBr>DEBT</ChrgBr>
                <CdtrAgt><FinInstnId><BICFI>{fields.get("57A", "")}</BICFI></FinInstnId></CdtrAgt>
                <Cdtr><Nm>{fields.get("59", "").splitlines()[0]}</Nm></Cdtr>
                <RmtInf><Ustrd>{fields.get("70", "")}</Ustrd></RmtInf>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""
