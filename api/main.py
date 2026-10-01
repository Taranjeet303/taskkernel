from fastapi import FastAPI

from api.routes import scripts, executions


app = FastAPI(title="TaskKernel", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}



app.include_router(
    scripts.router,
    tags=["Scripts"]
)

app.include_router(
    executions.router,
    tags=["Executions"]
)