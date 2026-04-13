import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Sniffer Analyzer API")


@app.get("/health")
def health():
    return {"status": "ok"}


def run():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)