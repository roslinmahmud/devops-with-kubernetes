from contextlib import asynccontextmanager
import json
import time
from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import requests
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    port = os.getenv("PORT", "8000")
    print(f"Server started in port {port}")
    yield

IMAGE_FILE = os.getenv("IMAGE_FILE", "files/cached_image.jpg")
METADATA_FILE = os.getenv("METADATA_FILE", "files/cache_metadata.json")
IMAGE_URL = os.getenv("IMAGE_URL", "https://picsum.photos/1200")
CACHE_DURATION = int(os.getenv("CACHE_DURATION", 600))
STATIC_DIR = os.getenv("STATIC_DIR", "files")
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "frontend")
HOST = os.getenv("HOST", "0.0.0.0")
DB_HOST = os.getenv("DB_HOST", "postgres-svc")
DB_NAME = os.getenv("DB_NAME", "tododb")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"timestamp": 0, "served_extra": False}

def save_metadata(metadata):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

def fetch_new_image():
    response = requests.get(IMAGE_URL)
    with open(IMAGE_FILE, "wb") as f:
        f.write(response.content)
    metadata = {"timestamp": time.time(), "served_extra": False}
    save_metadata(metadata)

app = FastAPI(lifespan=lifespan)

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/image")
async def get_image():
    metadata = load_metadata()
    current_time = time.time()

    if not os.path.exists(IMAGE_FILE):
        fetch_new_image()
    elif current_time - metadata["timestamp"] >= CACHE_DURATION:
        if metadata["served_extra"]:
            fetch_new_image()
        else:
            metadata["served_extra"] = True
            save_metadata(metadata)
    
    return {"image": "/static/cached_image.jpg"}

# Updated Todo model and database storage
class Todo(BaseModel):
    id: int = 0
    title: str
    completed: bool = False

@app.get("/api/todos")
async def get_todos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, completed FROM todos ORDER BY id ASC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.post("/api/todos")
async def create_todo(todo: Todo):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id, title, completed;",
        (todo.title, todo.completed)
    )
    new_todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_todo

# Serve Angular static files
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=HOST, port=port)