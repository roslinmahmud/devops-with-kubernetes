from contextlib import asynccontextmanager
import json
import time
from fastapi import FastAPI
import requests
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import HTMLResponse
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    port = os.getenv("PORT", 8000)
    print(f"Server started in port {port}")
    yield

IMAGE_FILE = "files/cached_image.jpg"
METADATA_FILE = "files/cache_metadata.json"

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"timestamp": 0, "served_extra": False}

def save_metadata(metadata):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

def fetch_new_image():
    response = requests.get("https://picsum.photos/1200")
    with open(IMAGE_FILE, "wb") as f:
        f.write(response.content)
    metadata = {"timestamp": time.time(), "served_extra": False}
    save_metadata(metadata)

app = FastAPI(lifespan=lifespan)

os.makedirs("files", exist_ok=True)

app.mount("/static", StaticFiles(directory="files"), name="static")

@app.get("/")
async def read_root():
    metadata = load_metadata()
    current_time = time.time()
    if not os.path.exists(IMAGE_FILE) or current_time - metadata["timestamp"] >= 600:  # 10 minutes
        if metadata["served_extra"]:
            fetch_new_image()
        else:
            metadata["served_extra"] = True
            save_metadata(metadata)
    
    html = """
    <!doctype html>
    <html>
      <head><title>Todo App</title></head>
      <body>
        <h1>Hello from FastAPI todo-app</h1>
        <img src="/static/cached_image.jpg" alt="Random Image" style="max-width: 100%; height: 60vh;">
        <h5>Devops with Kubernetes</h5>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)