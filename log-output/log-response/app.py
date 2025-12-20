import os
from datetime import datetime, UTC
from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse
from httpx import AsyncClient

app = FastAPI()

@app.get("/")
async def read_root():
    # read from log.txt the content
    with open("files/log.txt", "r") as f:
        lines = f.readlines()
    # # read from counter.txt the content
    # with open("files/counter.txt", "r") as f:
    #     counter_value = f.read().strip()
    async with AsyncClient() as client:
        response = await client.get("http://pingpong-svc:2346/pings")
        counter_value = response.json().get("counter", 0)
    content = f"{lines[-1].rstrip()}<br/>Ping / Pongs: {counter_value}"
    return HTMLResponse(content=content, media_type="text/html")

@app.get("/status")
async def get_status():
    # read from log.txt the content
    with open("files/log.txt", "r") as f:
        lines = f.readlines()
    return {"lines": lines[-10:]}  # return last 10 lines

if __name__ == "__main__":
    os.makedirs("files", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
