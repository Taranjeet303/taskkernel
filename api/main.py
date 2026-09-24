from fastapi import FastAPI
from api.routes.flow import router as flow_router
app = FastAPI(title="TaskKernel", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(flow_router)