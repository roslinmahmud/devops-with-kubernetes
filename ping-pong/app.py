import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

os.makedirs("files", exist_ok=True)

counter_file = "files/counter.txt"
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        try:
            last_value = int(f.read().strip())
            counter = last_value
        except ValueError:
            counter = 0
else:
    counter = 0

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Welcome to the Ping-Pong API!"


@app.get("/pingpong", response_class=PlainTextResponse)
async def ping():
    global counter
    value = counter
    counter += 1
    with open("files/counter.txt", "w") as f:
        f.write(f"{value}")
    return f"pong {value}"


@app.get("/pings")
async def get_pings():
    return {"counter": counter}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(8000))
