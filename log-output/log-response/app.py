import asyncio
import os
from datetime import datetime, UTC
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/status")
async def get_status():
    # read from log.txt the content
    with open("files/log.txt", "r") as f:
        lines = f.readlines()
    return {"lines": lines[-10:]}  # return last 10 lines

if __name__ == "__main__":
    os.makedirs("files", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
