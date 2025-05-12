from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from opcua import Client, ua

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# OPC UA connection details
SERVER_URL = "opc.tcp://10.10.10.3:9409/DvOpcUaServer"
SINGLE_TAG_NODE = "ns=2;s=0:ZZZ/AI1/SIMULATE.ENABLE"

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    try:
        opc_client = Client(SERVER_URL)
        opc_client.connect()
        node = opc_client.get_node(SINGLE_TAG_NODE)
        current_value = node.get_value()
        opc_client.disconnect()
    except Exception as e:
        current_value = f"Error: {e}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": "",
        "tags": [],
        "current_value": current_value
    })



from typing import Dict

@app.post("/write", response_class=HTMLResponse)
async def write_single_value(request: Request):
    form_data = await request.form()
    raw_val = form_data.get("sim_value", None)
    message = ""

    if raw_val is None:
        message = "No value provided."
    else:
        try:
            value = int(raw_val)
            #value = bool(raw_val)
            opc_client = Client(SERVER_URL)
            opc_client.connect()
            
            node = opc_client.get_node(SINGLE_TAG_NODE)
                    
            node.set_value(ua.Variant(value, ua.VariantType.UInt32))
            opc_client.disconnect()
            message = f"Wrote {value} to SIMULATE.ENABLE"
        except ValueError:
            message = "Invalid input — must be an integer."
        except Exception as e:
            message = f"Error: {e}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": message,
        "tags": []  # optional, if still in template
    })




from fastapi.responses import JSONResponse

@app.get("/read_tag")
async def read_single_tag():
    try:
        opc_client = Client(SERVER_URL)
        opc_client.connect()
        node = opc_client.get_node(SINGLE_TAG_NODE)
        value = node.get_value()
        opc_client.disconnect()
        return JSONResponse(content={"value": value})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})



