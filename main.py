from fastapi import FastAPI
from pydantic import BaseModel
from converters.mt_to_json import convert_mt_to_json
from converters.json_to_mx import convert_json_to_mx
from converters.mx_to_json import convert_mx_to_json
from converters.json_to_mt import convert_json_to_mt

app = FastAPI()

class RawMessage(BaseModel):
    message: str

class JSONMessage(BaseModel):
    data: dict

@app.post("/convert/mt/to/json")
def mt_to_json_api(payload: RawMessage):
    return {"jsonMT": convert_mt_to_json(payload.message)}

@app.post("/convert/jsonmt/to/mx")
def jsonmt_to_mx_api(payload: JSONMessage):
    return {"mx": convert_json_to_mx(payload.data)}

@app.post("/convert/mx/to/json")
def mx_to_json_api(payload: RawMessage):
    return {"jsonMX": convert_mx_to_json(payload.message)}

@app.post("/convert/jsonmx/to/mt")
def jsonmx_to_mt_api(payload: JSONMessage):
    return {"mt": convert_json_to_mt(payload.data)}
