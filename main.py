from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return "<h1>こんにちは世界</h1>"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
