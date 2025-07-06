# from fastapi import FastAPI, Request
# from fastapi.responses import PlainTextResponse, JSONResponse
#
# app = FastAPI()
#
#
# @app.post("/convert/mt101-to-pain001", response_class=PlainTextResponse)
# async def mt101_to_pain001(request: Request):
#     mt_text = (await request.body()).decode("utf-8")
#
#     def extract(tag):
#         for line in mt_text.splitlines():
#             if line.startswith(f":{tag}:"):
#                 return line[len(tag) + 2:].strip()
#         return ""
#
#     msg_id = extract("20")
#     sender = extract("50C")
#     receiver = extract("59")
#     amount = extract("32B").replace("GBP", "").replace(",", "").strip()
#
#     xml = f"""<Document>
#   <CstmrCdtTrfInitn>
#     <GrpHdr>
#       <MsgId>{msg_id}</MsgId>
#     </GrpHdr>
#     <PmtInf>
#       <Dbtr>
#         <Nm>{sender}</Nm>
#       </Dbtr>
#       <CdtTrfTxInf>
#         <Amt>
#           <InstdAmt Ccy="GBP">{amount}</InstdAmt>
#         </Amt>
#         <Cdtr>
#           <Nm>{receiver}</Nm>
#         </Cdtr>
#       </CdtTrfTxInf>
#     </PmtInf>
#   </CstmrCdtTrfInitn>
# </Document>"""
#
#     return xml
#
# @app.post("/convert/mt101-to-json", response_class=JSONResponse)
# async def mt101_to_json(request: Request):
#     mt_text = (await request.body()).decode("utf-8")
#     result = {}
#
#     # Extract only content inside {4:...-}
#     if "{4:" in mt_text and "-}" in mt_text:
#         mt_text = mt_text.split("{4:")[1].split("-}")[0]
#     else:
#         return {"error": "Invalid MT101 block: missing {4:...-}"}
#
#     current_tag = None
#     for line in mt_text.splitlines():
#         line = line.strip()
#         if line.startswith(":") and ":" in line[1:]:
#             parts = line[1:].split(":", 1)
#             current_tag = parts[0]
#             result[current_tag] = parts[1].strip()
#         elif current_tag:
#             result[current_tag] += " " + line.strip()
#
#     return result
from fastapi import FastAPI, Request, Body
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI()

@app.post("/convert/mt101-to-pain001", response_class=PlainTextResponse)
async def mt101_to_pain001(request: Request):
    mt_text = (await request.body()).decode("utf-8")

    def extract(tag):
        for line in mt_text.splitlines():
            if line.startswith(f":{tag}:"):
                return line[len(tag) + 2:].strip()
        return ""

    msg_id = extract("20")
    sender = extract("50C")
    receiver = extract("59")
    amount = extract("32B").replace("GBP", "").replace(",", "").strip()

    xml = f"""<Document>
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
    </GrpHdr>
    <PmtInf>
      <Dbtr>
        <Nm>{sender}</Nm>
      </Dbtr>
      <CdtTrfTxInf>
        <Amt>
          <InstdAmt Ccy="GBP">{amount}</InstdAmt>
        </Amt>
        <Cdtr>
          <Nm>{receiver}</Nm>
        </Cdtr>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>"""

    return xml

@app.post("/convert/mt101-to-json", response_class=JSONResponse)
async def mt101_to_json(body: str = Body(..., media_type="text/plain")):
    mt_text = body
    result = {}

    # Extract only content inside {4:...-}
    if "{4:" in mt_text and "-}" in mt_text:
        mt_text = mt_text.split("{4:")[1].split("-}")[0]
    else:
        return {"error": "Invalid MT101 block: missing {4:...-}"}

    current_tag = None
    for line in mt_text.splitlines():
        line = line.strip()
        if line.startswith(":") and ":" in line[1:]:
            parts = line[1:].split(":", 1)
            current_tag = parts[0]
            result[current_tag] = parts[1].strip()
        elif current_tag:
            result[current_tag] += " " + line.strip()

    return result
