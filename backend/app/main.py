from fastapi import FastAPI

app = FastAPI(title="Sniffer Analyzer API")


@app.get("/health")
def health():
    return {"status": "ok"}