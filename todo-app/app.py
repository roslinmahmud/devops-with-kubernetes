from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    port = os.getenv("PORT", 8000)
    print(f"Server started in port {port}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI todo-app"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)