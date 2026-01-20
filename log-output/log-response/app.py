import os
from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse
from httpx import AsyncClient

app = FastAPI()

@app.get("/")
async def read_root():
    # Read from information.txt
    with open("/etc/config/information.txt", "r") as f:
        file_content = f.read().strip()

    # Get MESSAGE env variable
    message = os.getenv("MESSAGE", "default message")

    # read from log.txt the content
    with open("files/log.txt", "r") as f:
        lines = f.readlines()

    # # read from counter.txt the content
    # with open("files/counter.txt", "r") as f:
    #     counter_value = f.read().strip()

    async with AsyncClient() as client:
        response = await client.get("http://pingpong-svc:2346/pings")
        counter_value = response.json().get("counter", 0)

    content = f"file content: {file_content}<br/>env variable: MESSAGE={message}<br/>{lines[-1].rstrip()}<br/>Ping / Pongs: {counter_value}"
    return HTMLResponse(content=content, media_type="text/html")

@app.get("/status")
async def get_status():
    # read from log.txt the content
    with open("files/log.txt", "r") as f:
        lines = f.readlines()
    return {"lines": lines[-10:]}  # return last 10 lines

@app.get("/healthz")
async def healthz():
    """Health check endpoint for readiness probe"""
    try:
        async with AsyncClient() as client:
            response = await client.get("http://pingpong-svc:2346/pings", timeout=2.0)
            if response.status_code == 200:
                return {"status": "healthy"}
            else:
                from fastapi import Response
                return Response(content=f"Ping-pong service returned {response.status_code}", status_code=503)
    except Exception as e:
        from fastapi import Response
        return Response(content=f"Cannot reach ping-pong service: {str(e)}", status_code=503)

if __name__ == "__main__":
    os.makedirs("files", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
