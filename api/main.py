from fastapi import FastAPI

app = FastAPI(title="TaskKernel", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}