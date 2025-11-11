from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from fastapi.responses import HTMLResponse
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    port = os.getenv("PORT", 8000)
    print(f"Server started in port {port}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    html = """
    <!doctype html>
    <html>
      <head><title>Todo App</title></head>
      <body><h1>Hello from FastAPI todo-app</h1></body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)