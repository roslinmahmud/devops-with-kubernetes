import os
from typing import Optional, Dict, Any, cast
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# DB connection setup
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "pingpong"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "password"),
}

def get_db_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        cursor_factory=RealDictCursor
    )

def init_db():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS counter (
                id SERIAL PRIMARY KEY,
                value INTEGER DEFAULT 0
            );
            INSERT INTO counter (value) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM counter);
        """)
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def get_counter():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM counter WHERE id = 1;")
        result = cast(Optional[Dict[str, Any]], cur.fetchone())
    conn.close()
    return result.get("value", 0) if result else 0

def update_counter(value):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE counter SET value = %s WHERE id = 1;", (value,))
    conn.commit()
    conn.close()

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Welcome to the Ping-Pong API!"


@app.get("/pingpong", response_class=PlainTextResponse)
async def ping():
    value = get_counter()
    update_counter(value + 1)
    return f"pong {value}"


@app.get("/pings")
async def get_pings():
    return {"counter": get_counter()}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(8000))
