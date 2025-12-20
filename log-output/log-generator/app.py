import asyncio
import os
import uuid
from datetime import datetime, UTC
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

random_string = str(uuid.uuid4())  # Generated on startup

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Application started with ID: {random_string}")
    # Start background task for logging
    task = asyncio.create_task(log_loop())
    yield
    # Shutdown: cancel the background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

os.makedirs("files", exist_ok=True)

async def log_loop():

    while True:
        timestamp = datetime.now(UTC).isoformat() + "Z"
        
        #write to file log.txt
        with open("files/log.txt", "a") as f:
            f.write(f"{timestamp}: {random_string}\n")
            
        # trim file to last 100 lines
        with open("files/log.txt", "r") as f:
            lines = f.readlines()
        if len(lines) > 100:
            with open("files/log.txt", "w") as f:
                f.writelines(lines[-100:])

        await asyncio.sleep(5)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
