import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager

import psycopg2
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

# Configure logging to stdout for Kubernetes
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    title: str = Field(..., max_length=140)
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
    logger.info(f"New todo received: {todo.title}")
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

@app.post("/api/todos/generate-wiki")
async def generate_wiki_todo():
    """Generate a todo with a random Wikipedia article"""
    try:
        # Get random Wikipedia article URL
        headers = {"User-Agent": "TodoApp/1.0 (Educational project)"}
        response = requests.get("https://en.wikipedia.org/wiki/Special:Random", headers=headers, allow_redirects=True)
        wiki_url = response.url
        
        # Create todo with the Wikipedia URL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        title = f"Read {wiki_url}"
        cur.execute(
            "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id, title, completed;",
            (title, False)
        )
        new_todo = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return new_todo
    except Exception as e:
        return {"error": str(e)}

@app.get("/healthz")
async def healthz():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.put("/api/todos/{todo_id}")
async def update_todo(todo_id: int, todo: Todo):
    """Update a todo's completed status"""
    logger.info(f"Updating todo {todo_id}: completed={todo.completed}")
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "UPDATE todos SET completed = %s WHERE id = %s RETURNING id, title, completed;",
        (todo.completed, todo_id)
    )
    updated_todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    if updated_todo is None:
        return JSONResponse(status_code=404, content={"error": "Todo not found"})
    
    return updated_todo

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Serve Angular static files
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=HOST, port=port)