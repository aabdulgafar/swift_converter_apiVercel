from fastapi import FastAPI
from pydantic import BaseModel
from converters.mt101_to_pain001 import (
    convert_mt101_to_pain001,
    convert_mt101_to_json,
    convert_json_to_pain001,
    convert_full_mt101_to_pain001,
    convert_full_mt101_to_json
)
from converters.mt103_to_pacs008 import (
    convert_mt103_to_pacs008,
    convert_mt103_to_json,
    convert_json_to_pacs008,
    convert_full_mt103_to_pacs008,
    convert_full_mt103_to_json
)

app = FastAPI()

class MTMessage(BaseModel):
    message: str

class JSONPayload(BaseModel):
    type: str
    fields: dict

def clean_input(message: str) -> str:
    return message.replace('\r\n', '\n').replace('\r', '\n').strip()

# --- Basic tag-level parsers ---
@app.post("/convert/mt101/to/pain001")
def mt101_to_pain001_api(data: MTMessage):
    return {"pain001": convert_mt101_to_pain001(clean_input(data.message))}

@app.post("/convert/mt101/to/json")
def mt101_to_json_api(data: MTMessage):
    return convert_mt101_to_json(clean_input(data.message))

@app.post("/convert/json/to/pain001")
def json_to_pain001_api(data: JSONPayload):
    return {"pain001": convert_json_to_pain001(data)}

@app.post("/convert/mt103/to/pacs008")
def mt103_to_pacs008_api(data: MTMessage):
    return {"pacs008": convert_mt103_to_pacs008(clean_input(data.message))}

@app.post("/convert/mt103/to/json")
def mt103_to_json_api(data: MTMessage):
    return convert_mt103_to_json(clean_input(data.message))

@app.post("/convert/json/to/pacs008")
def json_to_pacs008_api(data: JSONPayload):
    return {"pacs008": convert_json_to_pacs008(data)}

# --- Full block parsers ---
@app.post("/convert/mt101/full/to/pain001")
def mt101_full_to_pain001(data: MTMessage):
    return {"pain001": convert_full_mt101_to_pain001(clean_input(data.message))}

@app.post("/convert/mt101/full/to/json")
def mt101_full_to_json(data: MTMessage):
    return convert_full_mt101_to_json(clean_input(data.message))

@app.post("/convert/mt103/full/to/pacs008")
def mt103_full_to_pacs008(data: MTMessage):
    return {"pacs008": convert_full_mt103_to_pacs008(clean_input(data.message))}

@app.post("/convert/mt103/full/to/json")
def mt103_full_to_json(data: MTMessage):
    return convert_full_mt103_to_json(clean_input(data.message))
